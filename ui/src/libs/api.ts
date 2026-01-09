// src/libs/api.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from './auth';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// ========================================
// AXIOS INSTANCE
// ========================================
export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========================================
// TOKEN REFRESH LOGIC
// ========================================
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function onRefreshed(token: string) {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
}

function addRefreshSubscriber(callback: (token: string) => void) {
  refreshSubscribers.push(callback);
}

// ========================================
// REQUEST INTERCEPTOR
// ========================================
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { accessToken } = useAuthStore.getState();
    
    if (accessToken && config.headers) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    
    return config;
  },
  (error) => Promise.reject(error)
);

// ========================================
// RESPONSE INTERCEPTOR (AUTO-REFRESH)
// ========================================
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Si erreur 401 et pas déjà retenté
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      
      // Si c'est un refresh qui échoue, déconnecter
      if (originalRequest.url?.includes('/auth/refresh')) {
        console.error('❌ Refresh token expired, logging out...');
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(error);
      }

      originalRequest._retry = true;

      // Si refresh en cours, attendre
      if (isRefreshing) {
        return new Promise((resolve) => {
          addRefreshSubscriber((token: string) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            resolve(api(originalRequest));
          });
        });
      }

      isRefreshing = true;

      try {
        const { refreshToken } = useAuthStore.getState();
        
        if (!refreshToken) {
          throw new Error('No refresh token available');
        }

        console.log('🔄 Refreshing access token...');

        // Appeler l'endpoint refresh (sans interceptor pour éviter la boucle)
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        const { access_token, refresh_token } = response.data;

        console.log('✅ Token refreshed successfully');

        // Mettre à jour les tokens dans le store et localStorage
        useAuthStore.setState({
          accessToken: access_token,
          refreshToken: refresh_token,
        });

        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);

        // Notifier les subscribers
        onRefreshed(access_token);
        isRefreshing = false;

        // Retry la requête originale avec le nouveau token
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
        }
        return api(originalRequest);

      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        isRefreshing = false;
        refreshSubscribers = [];
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Extrait le code de statut HTTP d'une erreur Axios
 */
export function getErrorStatus(error: unknown): number | null {
  if (axios.isAxiosError(error)) {
    return error.response?.status ?? null;
  }
  return null;
}

// ========================================
// TYPES TYPESCRIPT (✅ COMPLÈTEMENT MIS À JOUR)
// ========================================

export interface Candidate {
  id?: number;
  full_name: string;
  fullname?: string;  // Alias
  email?: string;
  phone?: string;
}

export interface CVText {
  id?: number;
  status?: string;
  raw_text?: string;
}

export interface Application {
  id: number;
  offer_id: number;
  candidate_id: number;
  fullname: string;
  email: string;
  phone: string;
  status: ApplicationStatus;
  created_at: string;
  
  // Relations (optionnelles selon l'endpoint)
  candidate?: Candidate;
  offer?: JobOffer;
  cv_text?: CVText;
  parsed_cv?: ParsedCV;
  scoring?: Scoring;
}

export type ApplicationStatus = 
  | 'UPLOADING' 
  | 'EXTRACTING' 
  | 'EXTRACTED' 
  | 'SCORING' 
  | 'SCORED' 
  | 'ERROR'
  | 'PENDING'
  | 'SUCCESS'
  | 'FAILED';

export interface Scoring {
  id: number;
  overall_score: number;
  details: ScoringDetails;
  created_at: string;
}

export interface ScoringDetails {
  education_score?: number;
  experience_score?: number;
  skills_score?: number;
  language_score?: number;
  matching_skills?: string[];
  years_experience?: number;
  education?: string[];
  languages?: string[];
}

export interface ParsedCV {
  id: number;
  application_id: number;
  full_name?: string;
  email?: string;
  phone?: string;
  skills: string[];
  experience_years?: number;
  education: string[];
  languages: string[];
  matching_score: number;
  skills_score: number;
  experience_score: number;
  education_score: number;
  language_score: number;
  created_at: string;
  updated_at?: string;
}

// ✅ JOB OFFER COMPLÈTEMENT MIS À JOUR AVEC TOUS LES NOUVEAUX CHAMPS
export interface JobOffer {
  id: number;
  title: string;
  description: string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  deleted: boolean;
  
  // ✅ NOMS EXACTS backend
  required_skills: string[];
  nice_to_have_skills: string[];
  min_experience_years: number;
  required_education: string[];
  required_languages: string[];
  
  owner_id?: number;
  created_at?: string;
  updated_at?: string;
}


// ========================================
// APPLICATIONS API
// ========================================
export const applicationsApi = {
  /**
   * Récupère TOUTES les candidatures (avec relations optionnelles)
   */
  getAllApplications: async (includeRelations = true): Promise<Application[]> => {
    const params = new URLSearchParams();
    if (includeRelations) {
      params.append('include_job_offer', 'true');
      params.append('include_scoring', 'true');
    }
    
    const response = await api.get<Application[]>(
      `/applications?${params.toString()}`
    );
    return response.data;
  },

  /**
   * ✅ Récupère les candidatures pour une offre spécifique
   * C'est la méthode utilisée dans OfferDetail.tsx
   */
  getApplications: async (offerId: number): Promise<Application[]> => {
    console.log('🔍 API Call: GET /applications/offers/' + offerId);
    const response = await api.get<Application[]>(
      `/applications/offers/${offerId}`
    );
    console.log('📦 API Response:', response.data);
    return response.data;
  },

  /**
   * Récupère une candidature par ID
   */
  getApplicationById: async (id: number): Promise<Application> => {
    const response = await api.get<Application>(`/applications/${id}`);
    return response.data;
  },

  /**
   * Alias pour getApplications (compatibilité)
   */
  getApplicationsByOffer: async (offerId: number): Promise<Application[]> => {
    return applicationsApi.getApplications(offerId);
  },

  /**
   * Upload CV pour une candidature
   */
  uploadCV: async (offerId: number, formData: FormData): Promise<Application> => {
    const response = await api.post<Application>(
      `/applications/offers/${offerId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },
};

// ========================================
// JOB OFFERS API (✅ TYPES MIS À JOUR)
// ========================================
export const offersApi = {
  /**
   * Récupère toutes les offres
   */
  getOffers: async (): Promise<JobOffer[]> => {
    const response = await api.get<JobOffer[]>('/offers');
    return response.data;
  },

  /**
   * Récupère une offre par ID
   */
  getOffer: async (id: number): Promise<JobOffer> => {
    const response = await api.get<JobOffer>(`/offers/${id}`);
    return response.data;
  },

  /**
   * Crée une nouvelle offre (✅ avec tous les nouveaux champs)
   */
  createOffer: async (data: Omit<JobOffer, 'id' | 'created_at' | 'updated_at'>): Promise<JobOffer> => {
    const response = await api.post<JobOffer>('/offers', data);
    return response.data;
  },

  /**
   * Met à jour une offre
   */
  updateOffer: async (id: number, data: Partial<JobOffer>): Promise<JobOffer> => {
    const response = await api.patch<JobOffer>(`/offers/${id}`, data);
    return response.data;
  },

  /**
   * Supprime (archive) une offre
   */
  deleteOffer: async (id: number): Promise<void> => {
    await api.delete(`/offers/${id}`);
  },
};

// ========================================
// AUTH API
// ========================================
export const authApi = {
  /**
   * Connexion utilisateur
   */
  login: async (email: string, password: string) => {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  /**
   * Refresh token
   */
  refreshToken: async (refreshToken: string) => {
    const response = await axios.post(
      `${API_BASE_URL}/api/v1/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
  },

  /**
   * Récupère l'utilisateur connecté
   */
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },

  /**
   * Déconnexion (côté client)
   */
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_email');
  },
};

// ========================================
// EXPORTS LEGACY (pour compatibilité)
// ========================================
export const jobOffersApi = offersApi;  // Alias pour compatibilité
