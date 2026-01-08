import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { offersApi, JobOffer, getErrorStatus } from '@/lib/api';
import { useNavigate } from 'react-router-dom';


// Mock data pour fallback
const MOCK_OFFERS: JobOffer[] = [
  {
    id: 1,
    title: 'Développeur Python Senior',
    description: 'Développement backend Python / FastAPI / PostgreSQL.',
    status: 'PUBLISHED',
  },
  {
    id: 2,
    title: 'Data Scientist',
    description: 'Machine Learning, NLP, Python, MLOps.',
    status: 'PUBLISHED',
  },
  {
    id: 3,
    title: 'Ingénieur DevOps',
    description: 'Docker, Kubernetes, CI/CD, Cloud.',
    status: 'PUBLISHED',
  },
  {
    id: 4,
    title: 'Développeur Full Stack',
    description: 'React, TypeScript, FastAPI.',
    status: 'PUBLISHED',
  },
  {
    id: 5,
    title: 'Product Manager',
    description: 'Roadmap produit, Agile, coordination équipes.',
    status: 'DRAFT',
  },
];

export function OffersPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState('');

  // Query pour récupérer les offres
  const { data: offers = [], isLoading, error, refetch } = useQuery({
    queryKey: ['offers'],
    queryFn: offersApi.getOffers,
    retry: (failureCount, error) => {
      const status = getErrorStatus(error);
      console.log('[Offers Query] Retry:', failureCount, 'Status:', status);
      // Ne pas retry si 401
      return failureCount < 1 && status !== 401;
    },
  });

  // Mutation pour créer une offre
  const createMutation = useMutation({
    mutationFn: (offerData: Omit<JobOffer, 'id'>) =>
      offersApi.createOffer(offerData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['offers'] });
    },
    onError: (error) => {
      console.error('[Create Offer Error]:', error);
    },
  });

  // Mutation pour archiver une offre
  const deleteMutation = useMutation({
    mutationFn: offersApi.deleteOffer,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['offers'] });
    },
  });

  // Détermine les offres à afficher : vraies données OU mock si erreur
  const displayOffers: JobOffer[] =
    error && getErrorStatus(error) === 401 ? MOCK_OFFERS : offers;

  // Filtre les offres selon la recherche
  const filteredOffers = displayOffers.filter((offer) =>
    offer.title.toLowerCase().includes(search.toLowerCase())
  );

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

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold tracking-tight mb-2">
            Offres d'emploi
          </h1>
          <p className="text-muted-foreground text-lg">
            Gérez vos recrutements et candidatures
          </p>
        </div>
          <Button
            onClick={() => navigate('/offers/new')}
            size="lg"
          >
            + Nouvelle offre
          </Button>

      </div>

      {/* Debug panel si erreur 401 */}
      {error && getErrorStatus(error) === 401 && (
        <div className="mb-8 p-6 bg-orange-50 border border-orange-200 rounded-2xl">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-3 h-3 bg-orange-500 rounded-full animate-pulse"></div>
            <h3 className="font-semibold text-orange-900">API Backend (401)</h3>
          </div>
          <p className="text-orange-800 mb-4">
            Token JWT envoyé mais backend refuse. <br />
            <strong>Affichage des données de démonstration.</strong> <br />
            <small>Vérifier : CORS backend, migration DB, seed exécuté.</small>
          </p>
          <div className="flex space-x-2">
            <Button variant="outline" size="sm" onClick={() => refetch()}>
              🔄 Réessayer API
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                window.open('http://localhost:8000/docs', '_blank')
              }
            >
              🛠️ Swagger Backend
            </Button>
          </div>
        </div>
      )}

      {/* Barre de recherche */}
      <div className="mb-8">
        <Input
          placeholder="Rechercher une offre..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-md"
        />
      </div>

      {/* Tableau des offres */}
      <div className="bg-card border rounded-2xl overflow-hidden shadow-lg">
        {isLoading ? (
          <div className="p-16 text-center">
            <div className="animate-pulse bg-muted h-12 w-80 mx-auto mb-6 rounded-xl"></div>
            <p className="text-muted-foreground">Chargement des offres...</p>
          </div>
        ) : filteredOffers.length === 0 ? (
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
                d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
              />
            </svg>
            <h3 className="text-2xl font-semibold mb-2 text-muted-foreground">
              Aucune offre trouvée
            </h3>
            <Button
              onClick={() =>
                createMutation.mutate({
                  title: 'Ma première offre',
                  description: 'Commencez votre premier recrutement...',
                  status: 'DRAFT',
                })
              }
            >
              Créer la première
            </Button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-muted/50 border-b">
                <tr>
                  <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">
                    Titre
                  </th>
                  <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">
                    Statut
                  </th>
                  <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">
                    Description
                  </th>
                  <th className="px-8 py-4 text-right text-sm font-semibold text-muted-foreground">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filteredOffers.map((offer) => (
                  <tr
                    key={offer.id}
                    className="border-t hover:bg-muted/50 transition-colors"
                  >
                    <td className="px-8 py-6 font-semibold max-w-xs truncate">
                      {offer.title}
                    </td>
                    <td className="px-8 py-6">
                      <Badge className={statusColor(offer.status)}>
                        {offer.status}
                      </Badge>
                    </td>
                    <td className="px-8 py-6 text-sm text-muted-foreground max-w-md truncate">
                      {offer.description}
                    </td>
                    <td className="px-8 py-6">
                      <div className="flex items-center justify-end space-x-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => navigate(`/offers/${offer.id}`)}  // ✅ NOUVEAU
                        >
                          Détail
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteMutation.mutate(offer.id)}
                          disabled={deleteMutation.isPending}
                          className="text-destructive hover:text-destructive hover:bg-destructive/10"
                        >
                          {deleteMutation.isPending ? '...' : 'Archiver'}
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
