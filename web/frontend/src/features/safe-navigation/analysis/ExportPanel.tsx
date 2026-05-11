import { Download, FileSpreadsheet, FileText, Image as ImageIcon } from 'lucide-react';
import { useState } from 'react';
import type { MonteCarloResult } from '../types';
import { downloadFile, episodesToCsv, summaryToCsv, svgToPng } from './analysisHelpers';

export function ExportPanel({ result }: { result: MonteCarloResult }) {
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] = useState<string>('');

  const exportPng = async () => {
    setBusy(true);
    setFeedback('');
    try {
      const svgs = Array.from(document.querySelectorAll<SVGSVGElement>('.mc-page svg'));
      if (!svgs.length) {
        setFeedback('Nu există grafice de exportat. Deschide unul dintre tab-urile cu vizualizări înainte de export.');
        return;
      }
      let exported = 0;
      for (let index = 0; index < svgs.length; index += 1) {
        const svg = svgs[index];
        const dataUrl = await svgToPng(svg);
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `monte-carlo-chart-${index + 1}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        exported += 1;
      }
      setFeedback(`${exported} grafic(e) exportate ca PNG.`);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Eroare la export PNG.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="mc-card">
      <header className="mc-card__header">
        <div>
          <h2>Export pentru raport</h2>
          <p className="mc-card__caption">
            Descarcă rezumatul agregat și episoadele brute pentru analize externe sau anexa lucrării.
          </p>
        </div>
      </header>

      <div className="mc-export-row">
        <button
          type="button"
          className="secondary-button"
          title="Exportă câte un rând per agent, cu mediile, ratele și intervalele de încredere."
          onClick={() => downloadFile('monte-carlo-summary.csv', summaryToCsv(result))}
        >
          <FileSpreadsheet size={16} /> CSV rezumat agregat
        </button>
        <button
          type="button"
          className="secondary-button"
          title="Exportă fiecare episod individual, util pentru analize externe sau debugging."
          onClick={() => downloadFile('monte-carlo-episodes.csv', episodesToCsv(result))}
        >
          <FileText size={16} /> CSV episoade brute
        </button>
        <button
          type="button"
          className="secondary-button"
          title="Exportă configurația, profilul și rezumatul agregat în format JSON."
          onClick={() =>
            downloadFile(
              'monte-carlo-result.json',
              JSON.stringify({ summary: result.summary, config: result.config, profile: result.profile }, null, 2),
              'application/json',
            )
          }
        >
          <Download size={16} /> JSON rezumat
        </button>
        <button
          type="button"
          className="secondary-button"
          title="Exportă graficele SVG vizibile din pagina Monte Carlo ca imagini PNG."
          onClick={exportPng}
          disabled={busy}
        >
          <ImageIcon size={16} /> {busy ? 'Se exportă...' : 'PNG pentru fiecare grafic'}
        </button>
      </div>

      {feedback && <p className="mc-feedback">{feedback}</p>}
    </section>
  );
}
