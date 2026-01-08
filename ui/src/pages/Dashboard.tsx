import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

export function Dashboard() {
  const stats = [
    { label: 'Offres actives', value: 3, change: '+2', color: 'green' },
    { label: 'CV analysés', value: 47, change: '+12', color: 'blue' },
    { label: 'Score moyen', value: '78%', change: '+4%', color: 'orange' },
    { label: 'Top score', value: '94%', change: 'Nouveau', color: 'green' }
  ];

  return (
    <div>
      <div className="mb-12">
        <h1 className="text-4xl font-bold tracking-tight mb-2">Dashboard</h1>
        <p className="text-muted-foreground text-lg">Bienvenue dans votre espace recruteur</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {stats.map((stat, index) => (
          <div key={index} className="group bg-card border rounded-2xl p-8 hover:shadow-xl transition-all hover:-translate-y-1">
            <div className="flex items-baseline justify-between mb-2">
              <span className="text-3xl font-bold text-foreground">{stat.value}</span>
              <span className={`text-sm font-medium px-3 py-1 rounded-full bg-${stat.color}-100 text-${stat.color}-700`}>
                {stat.change}
              </span>
            </div>
            <p className="text-muted-foreground text-sm">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-12">
        <div className="bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20 rounded-2xl p-8">
          <h3 className="text-xl font-semibold mb-4">Nouvelle offre</h3>
          <p className="text-muted-foreground mb-6">Créez une nouvelle offre d'emploi en quelques clics</p>
          <Link to="/offers/new">
            <Button size="lg" className="w-full">+ Nouvelle offre</Button>
          </Link>
        </div>

        <div className="border-2 border-dashed border-muted rounded-2xl p-12 text-center group hover:border-primary/50 transition-colors">
          <div className="w-20 h-20 mx-auto mb-4 bg-muted rounded-2xl flex items-center justify-center group-hover:bg-primary/10 transition-colors">
            <svg className="w-10 h-10 text-muted-foreground group-hover:text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h3 className="text-xl font-semibold mb-2">Glisser-déposer CV</h3>
          <p className="text-muted-foreground mb-6 max-w-md mx-auto">
            Déposez jusqu'à 10 CV pour analyse automatique
          </p>
          <div className="space-x-3">
            <Link to="/offers">
              <Button variant="outline">Choisir offre</Button>
            </Link>
            <Button>Analyser CV</Button>
          </div>
        </div>
      </div>

      {/* Dernières candidatures */}
      <div className="bg-card border rounded-2xl overflow-hidden">
        <div className="p-8 border-b">
          <h3 className="text-2xl font-semibold mb-2">Dernières candidatures</h3>
          <p className="text-muted-foreground">Activité récente sur vos offres</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-t">
                <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">Candidat</th>
                <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">Offre</th>
                <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">Score</th>
                <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">Statut</th>
                <th className="px-8 py-4 text-left text-sm font-semibold text-muted-foreground">Date</th>
              </tr>
            </thead>
            <tbody>
              {[
                { name: 'Jean Dupont', offer: 'Dev Python Senior', score: 92, status: 'Shortlisté', date: 'Aujourd\'hui' },
                { name: 'Marie Martin', offer: 'Dev Python Senior', score: 78, status: 'À analyser', date: 'Aujourd\'hui' },
                { name: 'Pierre Dubois', offer: 'Dev Python Senior', score: 65, status: 'Rejeté', date: 'Hier' }
              ].map((item, index) => (
                <tr key={index} className="border-t hover:bg-muted/50 transition-colors">
                  <td className="px-8 py-6 font-medium">{item.name}</td>
                  <td className="px-8 py-6">{item.offer}</td>
                  <td className="px-8 py-6">
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                      item.score >= 80 ? 'bg-green-100 text-green-800' :
                      item.score >= 60 ? 'bg-orange-100 text-orange-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {item.score}%
                    </span>
                  </td>
                  <td className="px-8 py-6">
                    <span className="px-3 py-1 bg-accent text-accent-foreground rounded-full text-xs">
                      {item.status}
                    </span>
                  </td>
                  <td className="px-8 py-6 text-muted-foreground">{item.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
