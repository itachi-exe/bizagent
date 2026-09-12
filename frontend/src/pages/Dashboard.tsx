import useSWR from "swr";
import { DollarSign, MessageSquare, ShoppingCart } from "lucide-react";
import Navbar from "../components/Navbar";
import StatTile from "../components/StatTile";
import SalesChart from "../components/SalesChart";
import ActivityFeed from "../components/ActivityFeed";
import KnowledgeGapsPanel from "../components/KnowledgeGapsPanel";
import { api, type PendingOrder } from "../api/client";
import { useActivityStream } from "../hooks/useActivityStream";

const salesData = [
  { day: "Sun", value: 18 },
  { day: "Mon", value: 34 },
  { day: "Tue", value: 27 },
  { day: "Wed", value: 56, active: true },
  { day: "Thu", value: 42 },
  { day: "Fri", value: 68, active: true },
  { day: "Sat", value: 32 },
];

export default function Dashboard() {
  const { events } = useActivityStream();
  const { data } = useSWR("summary", api.getSummary);
  const pending = useSWR("pending", api.getPendingFulfillment);
  const summary = data ?? {};

  return (
    <main className="min-h-screen bg-[var(--app-bg)] text-[var(--app-ink)]">
      <Navbar />

      <div className="mx-auto max-w-7xl px-4 py-6 lg:px-10 lg:py-10">

        {/* Stat tiles */}
        <section className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
          <StatTile
            label="Net sales / 30 days"
            value={`₦${Number(summary.orders_total_ngn ?? 0).toLocaleString()}`}
            sublabel="From persisted orders"
            icon={DollarSign}
          />
          <StatTile
            label="Orders"
            value={summary.orders_today ?? summary.orders ?? 0}
            sublabel="Persisted orders"
            icon={ShoppingCart}
          />
          <StatTile
            label="Conversations today"
            value={summary.conversations_today ?? summary.conversations ?? 0}
            sublabel="Active sessions"
            icon={MessageSquare}
          />
        </section>

        {/* Main grid: chart + sidebar */}
        <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1fr_320px]">

          {/* Left: chart + activity */}
          <section className="app-panel p-5 sm:p-8">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="app-section-label">Performance</p>
                <h1 className="mt-3 text-2xl font-light text-[var(--app-ink)] sm:text-3xl">
                  Sales overview
                </h1>
              </div>
              <button className="app-btn-ghost shrink-0">Last 7 days</button>
            </div>
            <SalesChart data={salesData} />
            <ActivityFeed events={events} />
          </section>

          {/* Right: gaps + pending */}
          <aside className="flex flex-col gap-5 min-w-0">
            <KnowledgeGapsPanel events={events} />
            <PendingPanel orders={pending.data} />
          </aside>
        </div>
      </div>
    </main>
  );
}

function PendingPanel({ orders }: { orders?: PendingOrder[] | { orders: PendingOrder[] } }) {
  const mockRows = [
    { order_ref: "ORD-KA-1031", customer_name: "Kunle", items: "1x Langstroth Beehive", total_ngn: 35000 },
    { order_ref: "ORD-AB-1032", customer_name: "Amaka", items: "2x Bee Smoker", total_ngn: 17000 },
  ];
  const rows: PendingOrder[] = Array.isArray(orders)
    ? orders
    : (orders as { orders: PendingOrder[] })?.orders ?? mockRows;

  return (
    <section className="app-panel p-5 sm:p-6">
      <div className="mb-4 flex items-center justify-between gap-4">
        <h2 className="app-section-label">Pending fulfillment</h2>
        <span className="shrink-0 text-[10px] text-[var(--app-muted)]">{rows.length} awaiting</span>
      </div>

      {rows.length === 0 ? (
        <p className="border-t border-[var(--app-row-border)] pt-4 text-sm text-[var(--app-muted)]">
          No orders awaiting fulfillment.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[380px] text-left text-sm">
            <thead className="border-y border-[var(--app-row-border)]">
              <tr>
                <th className="app-section-label py-3 font-normal">Order</th>
                <th className="app-section-label py-3 font-normal">Customer</th>
                <th className="app-section-label py-3 text-right font-normal">Total</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((order, i) => (
                <tr key={order.id ?? i} className="border-b border-[var(--app-row-border)]">
                  <td className="py-3 text-[var(--app-ink)]">{order.order_ref}</td>
                  <td className="py-3 text-[var(--app-muted)]">{order.customer_name}</td>
                  <td className="py-3 text-right text-[var(--app-muted)]">
                    ₦{Number(order.total_ngn).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
