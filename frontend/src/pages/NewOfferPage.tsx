import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createOffer } from "../api/ats";

const NewOfferPage: React.FC = () => {
  const [title, setTitle] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const created = await createOffer({
        title,
        description,
        location,
        company_name: companyName,
      });
      navigate(`/offers/${created.id}`);
    } catch (err) {
      console.error(err);
      setError("Impossible de créer l'offre.");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-3xl mx-auto px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-800">
            Nouvelle offre
          </h1>
          <Link
            to="/offers"
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            ← Retour aux offres
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Titre
                </label>
                <input
                  className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">
                  Entreprise
                </label>
                <input
                  className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">
                Lieu
              </label>
              <input
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">
                Description
              </label>
              <textarea
                className="mt-1 w-full rounded border border-slate-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
                rows={6}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>

            {error && <div className="text-sm text-red-600">{error}</div>}

            <button
              type="submit"
              disabled={creating}
              className="px-4 py-2 rounded bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 disabled:opacity-60"
            >
              {creating ? "Création..." : "Créer l'offre"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
};

export default NewOfferPage;
