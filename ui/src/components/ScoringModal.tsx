import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { applicationsApi, Application } from '@/lib/api';

interface ScoringModalProps {
  application: Application;
  onClose: () => void;
}

export function ScoringModal({ application, onClose }: ScoringModalProps) {
  // ✅ FETCH SCORING DATA
  const { data: scoring, isLoading, error } = useQuery({
    queryKey: ['scoring', application.id],
    queryFn: async () => {
      console.log('📊 Fetching scoring for application:', application.id);
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/applications/${application.id}/scoring`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
          }
        );
        
        if (!response.ok) {
          console.error('❌ Scoring error:', response.status, response.statusText);
          throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        console.log('✅ Scoring data:', data);
        return data;
      } catch (err) {
        console.error('❌ Fetch error:', err);
        throw err;
      }
    },
  });

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full">
          <div className="flex items-center justify-center">
            <p className="text-muted-foreground">⏳ Chargement du scoring...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 max-w-md w-full">
          <h2 className="text-lg font-semibold mb-4 text-red-600">Erreur du scoring</h2>
          <p className="text-sm text-muted-foreground mb-6">
            {error instanceof Error ? error.message : 'Une erreur est survenue'}
          </p>
          <Button onClick={onClose} className="w-full">
            Fermer
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-8 max-w-2xl w-full max-h-96 overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold">Scoring - {application.candidate?.fullname}</h2>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground"
          >
            <X size={24} />
          </button>
        </div>

        {scoring && (
          <div className="space-y-6">
            {/* Score Global */}
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-6">
              <h3 className="text-sm font-semibold text-muted-foreground mb-2">Score Global</h3>
              <div className="flex items-center gap-4">
                <div className="text-5xl font-bold text-blue-600">
                  {Math.round(scoring.score)}%
                </div>
                <div className="flex-1">
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-blue-600 h-3 rounded-full transition-all"
                      style={{ width: `${scoring.score}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground mt-2">
                    {scoring.score >= 80
                      ? '✅ Excellent match'
                      : scoring.score >= 60
                      ? '⭐ Bon match'
                      : scoring.score >= 40
                      ? '⚠️ Match moyen'
                      : '❌ Faible match'}
                  </p>
                </div>
              </div>
            </div>

            {/* Détails candidat */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Candidat</p>
                <p className="font-semibold">{application.candidate?.fullname}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-xs text-muted-foreground mb-1">Email</p>
                <p className="font-semibold text-sm">{application.candidate?.email}</p>
              </div>
            </div>

            {/* Message */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm text-blue-900">
                <strong>Note:</strong> Ce score est basé sur l'analyse de chevauchement de mots
                entre la description d'offre et le CV extrait.
              </p>
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3 mt-8">
          <Button
            variant="outline"
            onClick={onClose}
            className="flex-1"
          >
            Voir CV (Bientôt)
          </Button>
          <Button
            onClick={onClose}
            className="flex-1"
          >
            Fermer
          </Button>
        </div>
      </div>
    </div>
  );
}
