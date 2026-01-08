import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScoringModal } from '@/components/ScoringModal';
import { applicationsApi, Application } from '@/lib/api';

export function ApplicationsPage() {
  const [search, setSearch] = useState('');
  const [selectedApplication, setSelectedApplication] = useState<Application | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [sortBy, setSortBy] = useState<'date' | 'score'>('date');

// Fetch all applications
const { data: applications = [], isLoading } = useQuery({
  queryKey: ['all-applications'],
  queryFn: async () => {
    try {
      const result = await applicationsApi.getAllApplications();
      return Array.isArray(result) ? result : [];
    } catch (error) {
      console.error('Erreur getAllApplications:', error);
      return [];
    }
  },
  refetchInterval: 5000,
});

  // Filter et sort
  const filteredApplications = applications
    .filter((app) => {
      const matchesSearch =
        app.fullname.toLowerCase().includes(search.toLowerCase()) ||
        app.email.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = !filterStatus || app.status === filterStatus;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      if (sortBy === 'score') {
        // Mock score pour démo (en vrai viendrait de DB)
        return 0;
      }
      return new Date(b.created_at || 0).getTime() - new Date(a.created_at || 0).getTime();
    });

  const statusColor = (status: string) => {
    switch (status) {
      case 'SCORED':
        return 'bg-green-100 text-green-800';
      case 'SCORING':
        return 'bg-blue-100 text-blue-800';
      case 'EXTRACTING':
      case 'EXTRACTED':
        return 'bg-yellow-100 text-yellow-800';
      case 'ERROR':
        return 'bg-red-100 text-red-800';
      case 'UPLOADING':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const statusLabel = (status: string) => {
    const labels: Record<string, string> = {
      UPLOADING: '📤 Upload',
      EXTRACTING: '🔄 Extraction',
      EXTRACTED: '✓ Extrait',
      SCORING: '⚙️ Scoring',
      SCORED: '✅ Scoring terminé',
      ERROR: '❌ Erreur',
    };
    return labels[status] || status;
  };

  // Stats
  const stats = {
    total: applications.length,
    scored: applications.filter((a) => a.status === 'SCORED').length,
    processing: applications.filter((a) =>
      ['UPLOADING', 'EXTRACTING', 'SCORING'].includes(a.status)
    ).length,
    errors: applications.filter((a) => a.status === 'ERROR').length,
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2">Candidatures</h1>
        <p className="text-muted-foreground text-lg">
          Toutes les candidatures avec scores IA
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-card border rounded-2xl p-6">
          <p className="text-sm text-muted-foreground mb-2">Total</p>
          <p className="text-3xl font-bold">{stats.total}</p>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-2xl p-6">
          <p className="text-sm text-green-900 font-semibold mb-2">✅ Scoring terminé</p>
          <p className="text-3xl font-bold text-green-600">{stats.scored}</p>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6">
          <p className="text-sm text-yellow-900 font-semibold mb-2">⏳ En cours</p>
          <p className="text-3xl font-bold text-yellow-600">{stats.processing}</p>
        </div>
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <p className="text-sm text-red-900 font-semibold mb-2">❌ Erreurs</p>
          <p className="text-3xl font-bold text-red-600">{stats.errors}</p>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="mb-8 space-y-4 bg-card border rounded-2xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="text-sm font-semibold mb-2 block">Rechercher</label>
            <Input
              placeholder="Nom ou email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full"
            />
          </div>

          {/* Status Filter */}
          <div>
            <label className="text-sm font-semibold mb-2 block">Statut</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background"
            >
              <option value="">Tous les statuts</option>
              <option value="SCORED">✅ Scoring terminé</option>
              <option value="SCORING">⚙️ En scoring</option>
              <option value="EXTRACTING">🔄 Extraction</option>
              <option value="UPLOADING">📤 Upload</option>
              <option value="ERROR">❌ Erreur</option>
            </select>
          </div>

          {/* Sort */}
          <div>
            <label className="text-sm font-semibold mb-2 block">Trier par</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'date' | 'score')}
              className="w-full px-4 py-2 border border-border rounded-lg bg-background"
            >
              <option value="date">Date (Récent)</option>
              <option value="score">Score (Élevé)</option>
            </select>
          </div>
        </div>

        <div className="pt-2 border-t border-border">
          <p className="text-sm text-muted-foreground">
            {filteredApplications.length} résultat{filteredApplications.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-card border rounded-2xl overflow-hidden">
        {isLoading ? (
          <div className="p-16 text-center animate-pulse">
            <div className="inline-block w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin"></div>
            <p className="mt-4 text-muted-foreground">Chargement...</p>
          </div>
        ) : filteredApplications.length === 0 ? (
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
                d="M20 21l-4.35-4.35M11 19a8 8 0 100-16 8 8 0 000 16z"
              />
            </svg>
            <p className="text-muted-foreground">Aucune candidature trouvée</p>
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
                  <th className="px-8 py-4 text-center text-sm font-semibold">Score</th>
                  <th className="px-8 py-4 text-left text-sm font-semibold">Date</th>
                  <th className="px-8 py-4 text-right text-sm font-semibold">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredApplications.map((app) => (
                  <tr key={app.id} className="border-t hover:bg-muted/50 transition-colors">
                    <td className="px-8 py-6 font-medium">{app.fullname}</td>
                    <td className="px-8 py-6 text-sm text-muted-foreground">{app.email}</td>
                    <td className="px-8 py-6 text-sm text-muted-foreground">{app.phone}</td>
                    <td className="px-8 py-6">
                      <Badge className={statusColor(app.status)}>
                        {statusLabel(app.status)}
                      </Badge>
                    </td>
                    <td className="px-8 py-6 text-center">
                      {app.status === 'SCORED' ? (
                        <span className="font-bold text-lg">--</span>
                      ) : ['UPLOADING', 'EXTRACTING', 'SCORING'].includes(app.status) ? (
                        <span className="text-sm text-yellow-600 animate-pulse">⏳</span>
                      ) : (
                        <span className="text-muted-foreground">--</span>
                      )}
                    </td>
                    <td className="px-8 py-6 text-sm text-muted-foreground">
                      {app.created_at
                        ? new Date(app.created_at).toLocaleDateString('fr-FR')
                        : '--'}
                    </td>
                    <td className="px-8 py-6 text-right">
                      {app.status === 'SCORED' && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => setSelectedApplication(app)}
                        >
                          📊 Détails
                        </Button>
                      )}
                      {['UPLOADING', 'EXTRACTING', 'SCORING'].includes(app.status) && (
                        <span className="text-sm text-muted-foreground">Traitement...</span>
                      )}
                      {app.status === 'ERROR' && (
                        <span className="text-sm text-destructive">Erreur</span>
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
