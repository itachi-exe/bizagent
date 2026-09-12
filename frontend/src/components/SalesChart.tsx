import { Bar, BarChart, Cell, ResponsiveContainer, XAxis } from "recharts";

type SalesDatum = { day: string; value: number; active?: boolean };

export default function SalesChart({ data }: { data: SalesDatum[] }) {
  return (
    <div className="mt-8 min-h-[260px]">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 12, right: 6, left: 6, bottom: 0 }}>
          <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: "#9a9a8a", fontSize: 12 }} dy={10} />
          <Bar dataKey="value" barSize={40} radius={0}>
            {data.map((entry, index) => (
              <Cell key={`${entry.day}-${index}`} fill={entry.active ? "#5a7a5a" : "#e2e4dc"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
