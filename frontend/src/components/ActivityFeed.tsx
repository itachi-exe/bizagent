import { motion, AnimatePresence } from 'framer-motion'
import type { ActivityEvent } from '../api/client'
const color = (type: string) => type === 'order_created' || type === 'quote_created' ? 'bg-green' : type === 'escalation_created' ? 'bg-red' : type === 'conversation_started' || type === 'message_received' ? 'bg-blue' : 'bg-primary'
const todayAt = (hours: number, minutes: number) => {
  const timestamp = new Date()
  timestamp.setHours(hours, minutes, 0, 0)
  return timestamp
}
const demoEvents: ActivityEvent[] = [
  { type: 'order_created', timestamp: todayAt(14, 32), summary: 'Order #BA-1024 created. 10x Langstroth Beehive. NGN 350,000' },
  { type: 'escalation_created', timestamp: todayAt(14, 28), summary: 'Escalation. Kunle requested 30% discount' },
  { type: 'quote_created', timestamp: todayAt(14, 15), summary: 'Quote Q-0043 sent. 5x Protective Suit. NGN 90,000' },
  { type: 'conversation_started', timestamp: todayAt(14, 2), summary: 'New conversation. Amaka Obi' },
  { type: 'order_created', timestamp: todayAt(13, 55), summary: 'Order #BA-1023 created. 2x Bee Smoker. NGN 17,000' },
]
export default function ActivityFeed({ events }: { events?: ActivityEvent[] | null }) {
  const rows = events === null || events === undefined ? null : events.length === 0 ? demoEvents : events
  return <section className="panel p-7"><div className="mb-5 flex items-center justify-between"><h2 className="text-xs uppercase tracking-[0.2em] text-[rgba(255,255,255,0.4)]">Live Activity</h2><span className="section-label">Streaming</span></div><div className="border-t border-border"><AnimatePresence initial={false}>{rows ? rows.map((event, i) => <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} key={event.id ?? `${event.timestamp}-${i}`} className="flex items-center gap-4 border-b border-border py-4 text-sm"><time className="w-11 font-mono text-xs text-[rgba(255,255,255,0.3)]">{new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time><span className={`h-1.5 w-1.5 shrink-0 rounded-none ${color(event.type)}`} /><span className="truncate text-[rgba(255,255,255,0.85)]">{event.summary}</span></motion.div>) : <div className="space-y-3 py-4"><div className="skeleton h-4 w-3/4" /><div className="skeleton h-4 w-2/3" /><div className="skeleton h-4 w-5/6" /></div>}</AnimatePresence></div></section>
}
