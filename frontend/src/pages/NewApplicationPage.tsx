import React, { useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { createApplication } from "../api/ats";

const NewApplicationPage: React.FC = () => {
  const { offerId } = useParams();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  if (!offerId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-red-600">Identifiant d’offre manquant.</div>
      </div>
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Veuillez sélectionner un fichier CV.");
      return;
    }
    setError(null);
    setSuccess(null);
    setCreating(true);
    try {
      await createApplication(Number(offerId), {
        full_name: fullName,
        email: email || undefined,
        phone: phone || undefined,
        file,
      });
      setSuccess(
        "Candidature créée. L’extraction du CV est en cours, le scoring sera mis à jour dans quelques instants.",
      );
      setFullName("");
      setEmail("");
      setPhone("");
      setFile(null);
      // redirection optionnelle :
      // navigate(`/offers/${offerId}`);
    } catch (err) {
      console.error(err);
      setError("Impossible de créer la candidature.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-800">
            Nouvelle candidature · Offre #{offerId}
          </h1>
          <Link
            to={`/offers/${offerId}`}
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            ← Retour au scoring
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Nom complet
                </label>
                <input
                  className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  type="email"
                  className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Téléphone
                </label>
                <input
                  className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  CV (pdf/docx/jpg/png)
                </label>
                <input
                  type="file"
                  className="mt-1 w-full text-sm"
                  onChange={(e) => {
                    const f = e.target.files?.[0] || null;
                    setFile(f);
                  }}
                  required
                />
              </div>
            </div>

            {error && <div className="text-sm text-red-600">{error}</div>}
            {success && (
              <div className="text-sm text-emerald-600">{success}</div>
            )}

            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 rounded bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-60"
            >
              {creating ? "Envoi..." : "Créer la candidature"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default NewApplicationPage;
