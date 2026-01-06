import { Briefcase, Users, TrendingUp, Clock } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface KPICardProps {
  title: string
  value: string | number
  description: string
  icon: React.ReactNode
}

function KPICard({ title, value, description, icon }: KPICardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <div className="text-muted-foreground">{icon}</div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">Tableau de bord</h1>
          <p className="text-muted-foreground">Bienvenue dans votre espace recruteur ATS-IA</p>
        </div>

        {/* KPI Grid */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <KPICard
            title="Offres actives"
            value="5"
            description="+2 cette semaine"
            icon={<Briefcase className="h-4 w-4" />}
          />
          <KPICard
            title="CV en attente"
            value="23"
            description="en cours d'analyse"
            icon={<Clock className="h-4 w-4" />}
          />
          <KPICard
            title="Candidatures"
            value="127"
            description="+15% vs mois dernier"
            icon={<Users className="h-4 w-4" />}
          />
          <KPICard
            title="Score moyen"
            value="78%"
            description="+3% ce mois"
            icon={<TrendingUp className="h-4 w-4" />}
          />
        </div>

        {/* Featured Section */}
        <Card>
          <CardHeader>
            <CardTitle>Meilleures candidatures</CardTitle>
            <CardDescription>Top 5 des CVs avec le meilleur score cette semaine</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Placeholder: Real data from API */}
              <p className="text-muted-foreground text-sm">Chargement des données...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
