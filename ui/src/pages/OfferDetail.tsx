import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { UploadZone } from '@/components/UploadZone';
import { ScoringModal } from '@/components/ScoringModal';
import { offersApi, applicationsApi, Application } from '@/libs/api';

export function OfferDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const offerId = parseInt(id || '0');
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);

  // Fetch offre
  const { data: offer, isLoading: offerLoading, error: offerError } = useQuery({
    queryKey: ['offer', offerId],
    queryFn: () => offersApi.getOffer(offerId),
    enabled: !!offerId,
    retry: 1,
  });

  // ✅ FETCH APPLICATIONS - FIXÉ
  const { 
    data: applications = [], 
    refetch: refetchApplications,
    isLoading: appsLoading,
    error: appsError
  } = useQuery({
    queryKey: ['applications', offerId],
    queryFn: async () => {
      try {
        console.log('📤 Fetching applications for offer:', offerId);
        const result = await applicationsApi.getApplications(offerId);
        console.log('📥 API Response:', result);
        
        // Assure que c'est un array
        if (Array.isArray(result)) {
          console.log(`✅ Got ${result.length} applications`);
          return result;
        } else if (result?.items) {
          console.log(`✅ Got ${result.items.length} applications (from items)`);
          return result.items;
        } else {
          console.warn('⚠️ Unexpected response format:', result);
          return [];
        }
      } catch (error) {
        console.error('❌ Error fetching applications:', error);
        return [];
      }
    },
    enabled: !!offerId,
    refetchInterval: (data) => {
      if (!Array.isArray(data) || data.length === 0) return false;
      const hasProcessing = data.some(
        (app: Application) => !['SCORED', 'ERROR'].includes(app.status)
      );
      console.log('🔄 Refetch:', hasProcessing ? '3s (processing)' : 'disabled');
      return hasProcessing ? 3000 : false;
    },
  });

  if (offerLoading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-12 bg-muted rounded-lg w-1/3"></div>
        <div className="h-32 bg-muted rounded-lg"></div>
      </div>
    );
  }

  if (offerError || !offer) {
    return (
      <div className="text-center py-20">
        <h1 className="text-2xl font-bold mb-4">❌ Offre non trouvée</h1>
        <p className="text-muted-foreground mb-6">
          {offerError?.message || 'Erreur lors du chargement'}
        </p>
        <Button onClick={() => navigate('/offers')}>Retour aux offres</Button>
      </div>
    );
  }

  const statusColor = (status: string) => {
    switch (status) {
      case 'PUBLISHED':
        return 'bg-green-100 text-green-800';
      case 'DRAFT':
        return 'bg-yellow-100 text-yellow-800';
      case 'ARCHIVED':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const appStatusColor = (status: string) => {
    switch (status) {
      case 'SCORED':
        return 'bg-green-100 text-green-800';
      case 'SUCCESS':
        return 'bg-green-100 text-green-800';
      case 'SCORING':
        return 'bg-blue-100 text-blue-800';
      case 'EXTRACTING':
      case 'EXTRACTED':
        return 'bg-yellow-100 text-yellow-800';
      case 'PENDING':
        return 'bg-purple-100 text-purple-800';
      case 'ERROR':
      case 'FAILED':
        return 'bg-red-100 text-red-800';
      case 'UPLOADING':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <Button variant="outline" onClick={() => navigate('/offers')} className="mb-4">
          ← Retour
        </Button>
        <h1 className="text-4xl font-bold mb-2">{offer.title}</h1>
        <div className="flex items-center space-x-3">
          <Badge className={statusColor(offer.status)}>
            {offer.status}
          </Badge>
          <span className="text-muted-foreground">
            {applications.length} candidature{applications.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Description */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-card border rounded-2xl p-8">
            <h2 className="text-xl font-semibold mb-4">Description</h2>
            <p className="whitespace-pre-line text-foreground/80 leading-relaxed">
              {offer.description}
            </p>
          </div>

          {/* Requirements */}
          <div className="bg-card border rounded-2xl p-8">
            <h2 className="text-xl font-semibold mb-4">Compétences requises</h2>
            {offer.requirements && offer.requirements.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {offer.requirements.map((skill) => (
                  <Badge key={skill} className="bg-primary/20 text-primary border border-primary/30">
                    {skill}
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">Aucune compétence requise spécifiée</p>
            )}
          </div>

          {/* Nice to have */}
          {offer.nice_to_have && offer.nice_to_have.length > 0 && (
            <div className="bg-card border rounded-2xl p-8">
              <h2 className="text-xl font-semibold mb-4">Compétences appréciées</h2>
              <div className="flex flex-wrap gap-2">
                {offer.nice_to_have.map((skill) => (
                  <Badge key={skill} className="bg-accent border border-accent">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Upload Zone */}
        <div className="lg:col-span-1">
          <div className="bg-card border rounded-2xl p-8 sticky top-8">
            <h2 className="text-xl font-semibold mb-6">Ajouter candidat</h2>
            <UploadZone offerId={offerId} onUploadSuccess={() => {
              console.log('✅ Upload success, refetching applications...');
              refetchApplications();
            }} />
          </div>
        </div>
      </div>

      {/* Applications Table */}
      <div className="bg-card border rounded-2xl overflow-hidden">
        <div className="p-8 border-b border-border">
          <h2 className="text-2xl font-bold">Candidatures ({applications.length})</h2>
        </div>

        {appsLoading && (
          <div className="p-16 text-center">
            <p className="text-muted-foreground">⏳ Chargement des candidatures...</p>
          </div>
        )}

        {applications.length === 0 && !appsLoading ? (
          <div className="p-16 text-center">
            <svg
              className="w-16 h-16 mx-auto mb-4 text-muted-foreground"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"
              />
            </svg>
            <p className="text-muted-foreground">Aucune candidature pour le moment</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <th className="px-8 py-4 text-left text-sm font-semibold">Candidat</th>
                  <th className="px-8 py-4 text-left text-sm font-semibold">Email</th>
                  <th className="px-8 py-4 text-left text-sm font-semibold">Téléphone</th>
                  <th className="px-8 py-4 text-left text-sm font-semibold">Statut</th>
                  <th className="px-8 py-4 text-right text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr key={app.id} className="border-t hover:bg-muted/50 transition-colors">
                    <td className="px-8 py-6 font-medium">{app.candidate?.fullname || 'N/A'}</td>
                    <td className="px-8 py-6 text-sm text-muted-foreground">{app.candidate?.email || 'N/A'}</td>
                    <td className="px-8 py-6 text-sm text-muted-foreground">{app.candidate?.phone || 'N/A'}</td>
                    <td className="px-8 py-6">
                      <Badge className={appStatusColor(app.cv_text?.status || 'PENDING')}>
                        {app.cv_text?.status || 'PENDING'}
                      </Badge>
                    </td>
                    <td className="px-8 py-6 text-right">
                      {['SUCCESS', 'SCORED'].includes(app.cv_text?.status || '') && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedApplication(app)}
                        >
                          📊 Voir scoring
                        </Button>
                      )}
                      {['PENDING', 'EXTRACTING', 'SCORING'].includes(app.cv_text?.status || '') && (
                        <span className="text-sm text-yellow-600 animate-pulse">⏳ Traitement...</span>
                      )}
                      {['ERROR', 'FAILED'].includes(app.cv_text?.status || '') && (
                        <span className="text-sm text-destructive">❌ Erreur</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Scoring Modal */}
      {selectedApplication && (
        <ScoringModal
          application={selectedApplication}
          onClose={() => setSelectedApplication(null)}
        />
      )}
    </div>
  );
}
