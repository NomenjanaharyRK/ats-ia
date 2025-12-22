import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getOfferScoring } from "../api/ats";
import type { ApplicationScore } from "../api/ats";

const OfferScoring: React.FC = () => {
  const { offerId } = useParams();
  const [scores, setScores] = useState<ApplicationScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

useEffect(() => {
  const load = async () => {
    if (!offerId) return; // pas d'ID → on ne fait rien

    const parsed = Number(offerId);
    if (!Number.isFinite(parsed)) {
      setError("Identifiant d’offre invalide.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await getOfferScoring(parsed);
      setScores(data);
    } catch (err) {
      console.error(err);
      setError("Impossible de charger le scoring.");
    } finally {
      setLoading(false);
    }
  };
  load();
}, [offerId]);

  if (!offerId) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-red-600">Identifiant d’offre manquant.</div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-100">
        <div className="text-slate-700">Chargement du scoring...</div>
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
            Scoring IA · Offre #{offerId}
          </h1>
          <Link
            to="/offers"
            className="text-sm text-indigo-600 hover:text-indigo-700"
          >
            ← Retour aux offres
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {scores.length === 0 ? (
          <div className="text-slate-600">
            Aucune candidature à scorer pour cette offre.
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-left text-slate-600 font-medium">
                    Rang
                  </th>
                  <th className="px-4 py-2 text-left text-slate-600 font-medium">
                    Candidat
                  </th>
                  <th className="px-4 py-2 text-left text-slate-600 font-medium">
                    Score
                  </th>
                </tr>
              </thead>
              <tbody>
                {scores.map((s, index) => {
                  let color = "bg-red-100 text-red-700";
                  if (s.score >= 70) color = "bg-emerald-100 text-emerald-700";
                  else if (s.score >= 40)
                    color = "bg-amber-100 text-amber-700";

                  return (
                    <tr
                      key={s.application_id}
                      className="border-t border-slate-100"
                    >
                      <td className="px-4 py-2 text-slate-700">
                        {index + 1}
                      </td>
                      <td className="px-4 py-2 text-slate-800">
                        {s.candidate_full_name}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`inline-flex min-w-[3rem] justify-center rounded-full px-3 py-1 text-xs font-semibold ${color}`}
                        >
                          {s.score}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
};

export default OfferScoring;
