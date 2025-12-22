import api from "./client";

/* ---------- Auth déjà présent ---------- */
export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string) {
  const params = new URLSearchParams();
  params.append("username", username);
  params.append("password", password);

  const res = await api.post<LoginResponse>("/auth/login", params, {
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
  return res.data;
}

/* ---------- Offres ---------- */

export interface Offer {
  id: number;
  title: string;
  description: string;
  location?: string | null;
  company_name?: string | null;
  deleted?: boolean;
}

export async function getOffers(): Promise<Offer[]> {
  const res = await api.get<Offer[]>("/offers");
  return res.data;
}

export interface CreateOfferInput {
  title: string;
  description: string;
  location?: string;
  company_name?: string;
}

export async function createOffer(input: CreateOfferInput): Promise<Offer> {
  const res = await api.post<Offer>("/offers", input);
  return res.data;
}

/* ---------- Scoring ---------- */

export interface ApplicationScore {
  application_id: number;
  candidate_full_name: string;
  score: number;
}

export async function getOfferScoring(
  offerId: number,
): Promise<ApplicationScore[]> {
  const res = await api.get<ApplicationScore[]>(
    `/offers/${offerId}/applications/scoring`,
  );
  return res.data;
}

/* ---------- Candidatures ---------- */

export interface CreateApplicationInput {
  full_name: string;
  email?: string;
  phone?: string;
  file: File;
}

export async function createApplication(
  offerId: number,
  input: CreateApplicationInput,
) {
  const formData = new FormData();
  formData.append("full_name", input.full_name);
  if (input.email) formData.append("email", input.email);
  if (input.phone) formData.append("phone", input.phone);
  formData.append("file", input.file);

  const res = await api.post(`/offers/${offerId}/applications`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
  return res.data;
}
