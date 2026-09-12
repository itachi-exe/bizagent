import { Bar, BarChart, Cell, ResponsiveContainer, XAxis } from "recharts";
import { useTheme } from "../context/ThemeContext";

type SalesDatum = { day: string; value: number; active?: boolean };

export default function SalesChart({ data }: { data: SalesDatum[] }) {
  const { theme } = useTheme();
  const activeColor = theme === "dark" ? "#6b9e6b" : "#5a7a5a";
  const inactiveColor = theme === "dark" ? "#2a2a2a" : "#e2e4dc";
  const tickColor = theme === "dark" ? "#888888" : "#9a9a8a";

  return (
    <div className="mt-8 min-h-[260px]">
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} margin={{ top: 12, right: 6, left: 6, bottom: 0 }}>
          <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: tickColor, fontSize: 12 }} dy={10} />
          <Bar dataKey="value" barSize={40} radius={0}>
            {data.map((entry, index) => (
              <Cell key={`${entry.day}-${index}`} fill={entry.active ? activeColor : inactiveColor} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
