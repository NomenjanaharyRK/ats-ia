import React, { useEffect, useState } from "react";
import { getOffers } from "../api/ats";
import type { Offer } from "../api/ats";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const OffersList: React.FC = () => {

  const [offers, setOffers] = useState<Offer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { logout, user } = useAuth();

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getOffers();
        setOffers(data);
      } catch (err) {
        console.error(err);
        setError("Impossible de charger les offres.");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-slate-700">Chargement des offres...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100">
<header className="bg-white border-b border-slate-200">
  <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
    <h1 className="text-xl font-semibold text-slate-800">
      ATS‑IA · Offres
    </h1>
    <div className="flex items-center gap-3 text-sm">
      <span className="text-slate-600">{user?.email}</span>
      <button
        onClick={logout}
        className="px-3 py-1 rounded bg-slate-200 hover:bg-slate-300 text-slate-800"
      >
        Déconnexion
      </button>
    </div>
  </div>
</header>


      <main className="max-w-6xl mx-auto px-4 py-8">
        <Link
          to="/offers/new"
          className="px-3 py-1.5 rounded bg-indigo-600 text-white hover:bg-indigo-700"
        >
          Nouvelle offre
        </Link>
        
        {offers.length === 0 ? (
          <div className="text-slate-600">Aucune offre pour le moment.</div>
        ) : (
          <div className="mt-4 grid gap-4 md:grid-cols-2">
            {offers.map((offer) => (
              <div
                key={offer.id}
                className="bg-white rounded-lg border border-slate-200 shadow-sm p-4 flex flex-col justify-between"
              >
                <div>
                  <h2 className="text-lg font-semibold text-slate-800">
                    {offer.title}
                  </h2>
                  {offer.company_name && (
                    <p className="text-sm text-slate-600">
                      {offer.company_name}
                    </p>
                  )}
                  {offer.location && (
                    <p className="text-sm text-slate-500 mt-1">
                      {offer.location}
                    </p>
                  )}
                  {offer.description && (
                    <p className="text-sm text-slate-600 mt-3 line-clamp-3">
                      {offer.description}
                    </p>
                  )}
                </div>
<div className="mt-4 flex justify-between items-center">
  <Link
    to={`/offers/${offer.id}`}
    className="inline-flex items-center px-3 py-1.5 rounded bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700"
  >
    Voir détail & scoring
  </Link>
  <Link
    to={`/offers/${offer.id}/apply`}
    className="inline-flex items-center px-3 py-1.5 rounded border border-slate-300 text-sm text-slate-700 hover:bg-slate-50"
  >
    Nouvelle candidature
  </Link>
</div>

              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default OffersList;
