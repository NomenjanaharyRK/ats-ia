import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface PDFViewerProps {
  url: string;
  filename: string;
  matchedKeywords?: string[];
  onClose: () => void;
}

export function PDFViewer({
  url,
  filename,
  matchedKeywords = [],
  onClose,
}: PDFViewerProps) {
  const [fullscreen, setFullscreen] = useState(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
  };

  return (
    <div className={`${fullscreen ? 'fixed inset-0 z-50' : ''} bg-black/50 ${fullscreen ? 'flex' : 'rounded-2xl'}`}>
      <div className={`${fullscreen ? 'w-full h-screen' : 'max-w-4xl w-full max-h-[90vh]'} bg-card rounded-2xl shadow-xl flex flex-col`}>
        {/* Header */}
        <div className="border-b border-border p-6 flex items-center justify-between">
          <div className="flex-1">
            <h2 className="text-xl font-bold">{filename}</h2>
            {matchedKeywords.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {matchedKeywords.slice(0, 5).map((kw) => (
                  <Badge key={kw} className="bg-green-100 text-green-800 text-xs">
                    {kw}
                  </Badge>
                ))}
                {matchedKeywords.length > 5 && (
                  <Badge className="bg-muted text-xs">
                    +{matchedKeywords.length - 5}
                  </Badge>
                )}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground text-2xl font-light"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className={`flex-1 overflow-auto bg-muted ${fullscreen ? 'p-4' : 'p-6'}`}>
          <iframe
            src={url}
            className={`${fullscreen ? 'w-full h-full' : 'w-full h-full'} rounded-lg bg-white`}
            title={filename}
            style={{ minHeight: '400px' }}
          />
        </div>

        {/* Footer */}
        <div className="border-t border-border p-6 flex justify-between">
          <p className="text-sm text-muted-foreground">
            📄 {filename}
          </p>
          <div className="space-x-2 flex items-center">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFullscreen(!fullscreen)}
            >
              {fullscreen ? '🔍 Réduire' : '🖥️ Plein écran'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
            >
              📥 Télécharger
            </Button>
            <Button variant="outline" size="sm" onClick={onClose}>
              Fermer
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
