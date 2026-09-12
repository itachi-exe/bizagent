import { AnimatePresence, motion } from "framer-motion";
import type { ActivityEvent } from "../api/client";

const color = (type: string) => type === "escalation_created" ? "bg-red-400" : type === "conversation_started" || type === "message_received" ? "bg-blue-400" : "bg-[#5a7a5a]";
const todayAt = (hours: number, minutes: number) => { const timestamp = new Date(); timestamp.setHours(hours, minutes, 0, 0); return timestamp; };
const demoEvents: ActivityEvent[] = [
  { type: "order_created", timestamp: todayAt(14, 32), summary: "Order #BA-1024 created. 10x Langstroth Beehive. NGN 350,000" },
  { type: "escalation_created", timestamp: todayAt(14, 28), summary: "Escalation. Kunle requested 30% discount" },
  { type: "quote_created", timestamp: todayAt(14, 15), summary: "Quote Q-0043 sent. 5x Protective Suit. NGN 90,000" },
  { type: "conversation_started", timestamp: todayAt(14, 2), summary: "New conversation. Amaka Obi" },
  { type: "order_created", timestamp: todayAt(13, 55), summary: "Order #BA-1023 created. 2x Bee Smoker. NGN 17,000" },
];
export default function ActivityFeed({ events }: { events?: ActivityEvent[] | null }) {
  const rows = events === null || events === undefined ? null : events.length === 0 ? demoEvents : events;
  return <section className="mt-7"><div className="mb-2 flex items-center justify-between"><h3 className="app-section-label">Recent activity</h3><span className="app-section-label text-[#5a7a5a]">Streaming</span></div><div><AnimatePresence initial={false}>{rows ? rows.map((event, i) => <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} key={event.id ?? `${event.timestamp}-${i}`} className="flex items-center gap-3 border-b border-[#f0ede6] py-3"><span className={`inline-block h-1.5 w-1.5 shrink-0 rounded-full ${color(event.type)}`} /><time className="w-10 font-mono text-xs text-[#9a9a8a]">{new Date(event.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</time><span className="truncate text-sm text-[#1a1a1a]">{event.summary}</span></motion.div>) : <div className="space-y-3 py-4"><div className="h-4 w-3/4 animate-pulse bg-[#f0ede6]" /><div className="h-4 w-2/3 animate-pulse bg-[#f0ede6]" /></div>}</AnimatePresence></div></section>;
}
