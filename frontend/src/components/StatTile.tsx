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
        <div className="flex h-8 w-8 items-center justify-center rounded-sm border border-[#e8e6e0] text-[#5a7a5a]">
          <Icon size={17} />
        </div>
      </div>
      <div className="mt-4 text-4xl font-light tracking-tight text-[#1a1a1a]">{value}</div>
      {sublabel && <div className="mt-2 text-xs text-[#9a9a8a]">{sublabel}</div>}
    </div>
  );
}
