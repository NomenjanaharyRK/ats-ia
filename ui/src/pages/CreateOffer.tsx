import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { offersApi, JobOffer } from '@/lib/api';

const JOB_SKILLS = [
  'Python',
  'JavaScript',
  'TypeScript',
  'React',
  'FastAPI',
  'PostgreSQL',
  'Docker',
  'Kubernetes',
  'CI/CD',
  'AWS',
  'GCP',
  'Azure',
  'Git',
  'Linux',
  'Agile',
  'Scrum',
  'Machine Learning',
  'NLP',
  'TensorFlow',
  'PyTorch',
];

export function CreateOfferPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'DRAFT' as 'DRAFT' | 'PUBLISHED',
    requirements: [] as string[],
    nice_to_have: [] as string[],
  });

  const [showRequirementsDropdown, setShowRequirementsDropdown] = useState(false);
  const [showNiceToHaveDropdown, setShowNiceToHaveDropdown] = useState(false);

  // Mutation créer offre
  const createMutation = useMutation({
    mutationFn: (data: Omit<JobOffer, 'id'>) => offersApi.createOffer(data),
    onSuccess: () => {
      toast.success('✅ Offre créée avec succès !');
      queryClient.invalidateQueries({ queryKey: ['offers'] });
      setTimeout(() => navigate('/offers'), 1500);
    },
    onError: (error: any) => {
      const message =
        error?.response?.data?.detail || 'Erreur lors de la création';
      toast.error(`❌ ${message}`);
    },
  });

  // Handlers
  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddSkill = (skill: string, type: 'requirements' | 'nice_to_have') => {
    setFormData((prev) => {
      const current = prev[type];
      if (current.includes(skill)) {
        return {
          ...prev,
          [type]: current.filter((s) => s !== skill),
        };
      } else {
        return {
          ...prev,
          [type]: [...current, skill],
        };
      }
    });
  };

  const handleRemoveSkill = (skill: string, type: 'requirements' | 'nice_to_have') => {
    setFormData((prev) => ({
      ...prev,
      [type]: prev[type].filter((s) => s !== skill),
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.title.trim()) {
      toast.error('❌ Le titre est requis');
      return;
    }
    if (!formData.description.trim()) {
      toast.error('❌ La description est requise');
      return;
    }

    // Soumission
    createMutation.mutate(formData as Omit<JobOffer, 'id'>);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold tracking-tight mb-2">
          Créer une nouvelle offre
        </h1>
        <p className="text-muted-foreground text-lg">
          Remplissez les informations pour créer une offre d'emploi
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Titre */}
        <div className="space-y-3">
          <label className="text-sm font-semibold">
            Titre de l'offre *
          </label>
          <Input
            name="title"
            placeholder="ex: Développeur Python Senior"
            value={formData.title}
            onChange={handleInputChange}
            className="text-base"
          />
          <p className="text-xs text-muted-foreground">
            Soyez spécifique pour attirer les bons candidats
          </p>
        </div>

        {/* Description */}
        <div className="space-y-3">
          <label className="text-sm font-semibold">
            Description du poste *
          </label>
          <textarea
            name="description"
            placeholder="Décrivez le rôle, les responsabilités et l'environnement de travail..."
            value={formData.description}
            onChange={handleInputChange}
            rows={6}
            className="w-full px-4 py-3 border border-border rounded-lg bg-background text-base font-sans focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none"
          />
          <p className="text-xs text-muted-foreground">
            Incluez les détails importants : mission, environnement technique, localisation
          </p>
        </div>

        {/* Status */}
        <div className="space-y-3">
          <label className="text-sm font-semibold">
            Statut *
          </label>
          <select
            name="status"
            value={formData.status}
            onChange={handleInputChange}
            className="w-full px-4 py-3 border border-border rounded-lg bg-background text-base focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          >
            <option value="DRAFT">Brouillon (non visible)</option>
            <option value="PUBLISHED">Publié (visible aux candidats)</option>
          </select>
          <p className="text-xs text-muted-foreground">
            Les brouillons ne sont pas visibles sur le portail
          </p>
        </div>

        {/* Requirements */}
        <div className="space-y-3">
          <label className="text-sm font-semibold">
            Compétences requises
          </label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowRequirementsDropdown(!showRequirementsDropdown)}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background text-left focus:outline-none focus:ring-2 focus:ring-primary flex items-center justify-between"
            >
              <span className="text-muted-foreground">
                {formData.requirements.length > 0
                  ? `${formData.requirements.length} sélectionné(s)`
                  : 'Sélectionner les compétences requises'}
              </span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
              </svg>
            </button>

            {showRequirementsDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-10 max-h-80 overflow-y-auto">
                {JOB_SKILLS.map((skill) => (
                  <label
                    key={skill}
                    className="flex items-center space-x-3 px-4 py-3 hover:bg-accent cursor-pointer border-b border-border last:border-b-0"
                  >
                    <input
                      type="checkbox"
                      checked={formData.requirements.includes(skill)}
                      onChange={() =>
                        handleAddSkill(skill, 'requirements')
                      }
                      className="w-4 h-4 rounded"
                    />
                    <span className="text-sm">{skill}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Selected requirements */}
          {formData.requirements.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {formData.requirements.map((skill) => (
                <div
                  key={skill}
                  className="inline-flex items-center space-x-2 px-3 py-1 bg-primary/10 border border-primary/30 rounded-full text-sm"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill, 'requirements')}
                    className="ml-1 text-primary/60 hover:text-primary"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Nice to have */}
        <div className="space-y-3">
          <label className="text-sm font-semibold">
            Compétences appréciées
          </label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowNiceToHaveDropdown(!showNiceToHaveDropdown)}
              className="w-full px-4 py-3 border border-border rounded-lg bg-background text-left focus:outline-none focus:ring-2 focus:ring-primary flex items-center justify-between"
            >
              <span className="text-muted-foreground">
                {formData.nice_to_have.length > 0
                  ? `${formData.nice_to_have.length} sélectionné(s)`
                  : 'Sélectionner les compétences appréciées'}
              </span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                />
              </svg>
            </button>

            {showNiceToHaveDropdown && (
              <div className="absolute top-full left-0 right-0 mt-2 bg-card border border-border rounded-lg shadow-lg z-10 max-h-80 overflow-y-auto">
                {JOB_SKILLS.map((skill) => (
                  <label
                    key={skill}
                    className="flex items-center space-x-3 px-4 py-3 hover:bg-accent cursor-pointer border-b border-border last:border-b-0"
                  >
                    <input
                      type="checkbox"
                      checked={formData.nice_to_have.includes(skill)}
                      onChange={() =>
                        handleAddSkill(skill, 'nice_to_have')
                      }
                      className="w-4 h-4 rounded"
                    />
                    <span className="text-sm">{skill}</span>
                  </label>
                ))}
              </div>
            )}
          </div>

          {/* Selected nice to have */}
          {formData.nice_to_have.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {formData.nice_to_have.map((skill) => (
                <div
                  key={skill}
                  className="inline-flex items-center space-x-2 px-3 py-1 bg-accent border border-accent rounded-full text-sm"
                >
                  <span>{skill}</span>
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill, 'nice_to_have')}
                    className="ml-1 text-foreground/60 hover:text-foreground"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Form actions */}
        <div className="flex items-center space-x-4 pt-8 border-t border-border">
          <Button
            type="submit"
            disabled={createMutation.isPending}
            size="lg"
          >
            {createMutation.isPending ? 'Création en cours...' : '✓ Créer l\'offre'}
          </Button>
          <Button
            type="button"
            variant="outline"
            size="lg"
            onClick={() => navigate('/offers')}
            disabled={createMutation.isPending}
          >
            Annuler
          </Button>
        </div>
      </form>
    </div>
  );
}
