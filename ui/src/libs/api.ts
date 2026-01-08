import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Export du client
export const apiClient = api;

// Types
export interface JobOffer {
  id: number;
  title: string;
  description: string;
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
  requirements?: string[];
  nice_to_have?: string[];
  created_at?: string;
  updated_at?: string;
}

// API Offers
export const offersApi = {
  // Lister les offres
  getOffers: async () => {
    const response = await apiClient.get<JobOffer[]>('/api/v1/offers');
    return response.data;
  },

  // Créer une offre
  createOffer: async (data: Omit<JobOffer, 'id'>) => {
    const response = await apiClient.post<JobOffer>('/api/v1/offers', data);
    return response.data;
  },

  // Récupérer une offre
  getOffer: async (id: number) => {
    const response = await apiClient.get<JobOffer>(
      `/api/v1/offers/${id}`
    );
    return response.data;
  },

  // Mettre à jour une offre
  updateOffer: async (id: number, data: Partial<JobOffer>) => {
    const response = await apiClient.patch<JobOffer>(`/api/v1/offers/${id}`, data);
    return response.data;
  },

  // Archiver une offre
  deleteOffer: async (id: number) => {
    const response = await apiClient.delete(`/api/v1/offers/${id}`);
    return response.data;
  },
};

export interface Application {
  id: number;
  offer_id: number;
  fullname: string;
  email: string;
  phone: string;
  cv_file_id?: number;
  status: 'UPLOADING' | 'EXTRACTING' | 'EXTRACTED' | 'SCORING' | 'SCORED' | 'ERROR';
  task_id?: string;
  created_at?: string;
  updated_at?: string;
}

export interface Scoring {
  id: number;
  application_id: number;
  tfidf_score: number;
  sbert_score: number;
  quality_score: number;
  final_score: number;
  matched_skills: string[];
  missing_skills: string[];
  sections_detected: Record<string, any>;
  recommendations: string[];
}

export const applicationsApi = {
  // Upload CV
  uploadCV: async (offerId: number, formData: FormData) => {
    const response = await apiClient.post<Application>(
      `/api/v1/offers/${offerId}/applications`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },

  // Get applications pour une offre ✅ RETOURNE L'ARRAY
  getApplications: async (offerId: number) => {
    const response = await apiClient.get<Application[]>(
      `/api/v1/offers/${offerId}/applications`
    );
    // Si API retourne {data: [...]} vs directement [...]
    return Array.isArray(response.data) ? response.data : response.data?.data || [];
  },

  // Get status d'une application
  getApplicationStatus: async (applicationId: number) => {
    const response = await apiClient.get<Application>(
      `/api/v1/applications/${applicationId}`
    );
    return response.data;
  },

  // Get scoring détail
  getScoring: async (applicationId: number) => {
    const response = await apiClient.get<any>(
      `/api/v1/applications/${applicationId}/scoring`
    );
    return response.data;
  },

  // Get tous applications (global)
  getAllApplications: async () => {
    const response = await apiClient.get<Application[]>('/api/v1/applications');
    return Array.isArray(response.data) ? response.data : response.data?.data || [];
  },
};



// Utilitaire pour extraire le statut HTTP d'une erreur
export function getErrorStatus(error: unknown): number | null {
  if (axios.isAxiosError(error)) {
    return error.response?.status ?? null;
  }
  return null;
}
