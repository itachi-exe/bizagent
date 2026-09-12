export default function StatTile({
  value,
  label,
  detail,
}: {
  value: string | number;
  label: string;
  detail?: string;
}) {
  return (
    <div className="border-r border-border px-8 py-8 last:border-r-0">
      <div className="text-4xl font-light tracking-tight text-primary">
        {value}
      </div>
      <div className="section-label mt-3">{label}</div>
      {detail && <div className="mt-1 text-xs text-secondary">{detail}</div>}
    </div>
  );
}
