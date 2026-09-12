import type { LucideIcon } from "lucide-react";

export default function StatTile({
  value,
  label,
  sublabel,
  icon: Icon,
}: {
  value: string | number;
  label: string;
  sublabel?: string;
  icon: LucideIcon;
}) {
  return (
    <div className="app-panel w-full p-6">
      <div className="flex items-start justify-between">
        <div className="app-section-label">{label}</div>
        <div className="flex h-8 w-8 items-center justify-center rounded-sm border border-[var(--app-border)] text-[var(--app-olive)]">
          <Icon size={17} />
        </div>
      </div>
      <div className="mt-4 text-4xl font-light tracking-tight text-[var(--app-ink)]">{value}</div>
      {sublabel && <div className="mt-2 text-xs text-[var(--app-muted)]">{sublabel}</div>}
    </div>
  );
}
