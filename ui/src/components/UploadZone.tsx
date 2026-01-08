import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import toast from 'react-hot-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { applicationsApi } from '@/lib/api';

interface UploadZoneProps {
  offerId: number;
  onUploadSuccess?: () => void;
}

export function UploadZone({ offerId, onUploadSuccess }: UploadZoneProps) {
  const queryClient = useQueryClient();
  const [isDragging, setIsDragging] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
  });

  const uploadMutation = useMutation({
    mutationFn: (data: FormData) => {
      // ✅ Debug: log FormData
      console.log('📤 FormData contents:');
      data.forEach((value, key) => {
        if (value instanceof File) {
          console.log(`  ${key}: File(${value.name}, ${value.size} bytes, ${value.type})`);
        } else {
          console.log(`  ${key}: ${value}`);
        }
      });
      return applicationsApi.uploadCV(offerId, data);
    },
    onSuccess: (response) => {
      console.log('✅ Upload success:', response);
      toast.success('✅ CV uploadé ! Analyse en cours...');
      queryClient.invalidateQueries({ queryKey: ['applications', offerId] });
      setFormData({ full_name: '', email: '', phone: '' });
      onUploadSuccess?.();
    },
    onError: (error: any) => {
      console.error('❌ Upload error:', error);
      console.error('Error response:', error?.response?.data);
      const message =
        error?.response?.data?.detail ||
        error?.response?.data?.message ||
        error?.message ||
        'Erreur lors de l\'upload';
      toast.error(`❌ ${message}`);
    },
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    const file = files[0];
    if (!file) return;

    console.log('📄 File selected:', {
      name: file.name,
      size: file.size,
      type: file.type,
    });

    // Validation format
    const allowedFormats = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'image/png',      // ✅ NOUVEAU
      'image/jpeg',     // ✅ NOUVEAU
      'image/jpg',      // ✅ NOUVEAU
    ];
    if (!allowedFormats.includes(file.type)) {
      toast.error('❌ Format non supporté\n\nFormats acceptés:\n• PDF\n• DOCX, DOC\n• TXT\n• PNG, JPEG, JPG');
      return;
    }

    // Validation taille
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
      toast.error('❌ Fichier trop volumineux (max 10MB)');
      return;
    }

    // Validation form
    if (!formData.full_name.trim()) {
      toast.error('❌ Nom requis');
      return;
    }
    if (!formData.email.trim()) {
      toast.error('❌ Email requis');
      return;
    }
    if (!formData.phone.trim()) {
      toast.error('❌ Téléphone requis');
      return;
    }

    // Valide email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      toast.error('❌ Email invalide');
      return;
    }

    // Build FormData
    const data = new FormData();
    data.append('full_name', formData.full_name.trim());
    data.append('email', formData.email.trim().toLowerCase());
    data.append('phone', formData.phone.trim());
    data.append('file', file);

    uploadMutation.mutate(data);
  };

  return (
    <div className="space-y-6">
      {/* Form fields */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="space-y-2">
          <label className="text-sm font-semibold">Nom complet *</label>
          <Input
            name="full_name"
            placeholder="Jean Dupont"
            value={formData.full_name}
            onChange={handleInputChange}
            disabled={uploadMutation.isPending}
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold">Email *</label>
          <Input
            name="email"
            type="email"
            placeholder="jean@example.com"
            value={formData.email}
            onChange={handleInputChange}
            disabled={uploadMutation.isPending}
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold">Téléphone *</label>
          <Input
            name="phone"
            placeholder="+33 6 12 34 56 78"
            value={formData.phone}
            onChange={handleInputChange}
            disabled={uploadMutation.isPending}
          />
        </div>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-2xl p-12 text-center transition-all ${
          isDragging
            ? 'border-primary bg-primary/5'
            : 'border-border bg-muted/50 hover:border-primary/50'
        } ${uploadMutation.isPending ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
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
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10"
          />
        </svg>

        <h3 className="text-xl font-semibold mb-2">Déposez votre CV ici</h3>
        <p className="text-muted-foreground mb-4">
          ou{' '}
          <label className="text-primary cursor-pointer hover:underline">
            parcourez votre ordinateur
            <input
              type="file"
              className="hidden"
              accept=".pdf,.docx,.doc,.txt,.png,.jpg,.jpeg"
              onChange={handleFileChange}
              disabled={uploadMutation.isPending}
            />
          </label>
        </p>
        <p className="text-xs text-muted-foreground">
          PDF, DOCX, DOC, TXT, PNG, JPEG • Max 10MB
        </p>
      </div>

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-900 space-y-2">
        <p className="font-semibold">ℹ️ Formats supportés:</p>
        <ul className="text-xs space-y-1 ml-4 list-disc">
          <li><strong>Documents:</strong> PDF, DOCX, DOC, TXT</li>
          <li><strong>Images:</strong> PNG, JPEG (extraction via OCR)</li>
          <li><strong>Taille:</strong> Maximum 10 MB</li>
          <li><strong>Traitement:</strong> Peut prendre jusqu'à 1 minute</li>
        </ul>
      </div>

      {/* Progress */}
      {uploadMutation.isPending && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Envoi en cours...</span>
            <span className="text-sm text-muted-foreground">⏳</span>
          </div>
          <div className="w-full bg-muted rounded-full h-2 overflow-hidden">
            <div className="h-full bg-primary animate-pulse rounded-full" />
          </div>
        </div>
      )}

      {/* Error */}
      {uploadMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-sm text-red-900">
            <strong>Erreur:</strong> {uploadMutation.error?.message}
          </p>
        </div>
      )}
    </div>
  );
}
