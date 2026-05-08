import { BookOpen } from 'lucide-react';

export function ExplanationPanel({ text }: { text?: string }) {
  return (
    <section className="panel-card explanation-panel">
      <h2><BookOpen size={18} /> Educational Explanation</h2>
      <p>{text || 'Select an algorithm and run an episode to see how this strategy behaves in the simulator.'}</p>
    </section>
  );
}
