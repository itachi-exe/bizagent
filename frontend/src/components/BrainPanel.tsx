import useSWR from "swr";
import { api, type Product } from "../api/client";

const money = (n?: number) => `₦${(n ?? 0).toLocaleString()}`;

const fallbackBrain = {
  products: [
    { name: "Langstroth Beehive", price: 35000 },
    { name: "Protective Suit", price: 18000 },
    { name: "Bee Smoker", price: 8500 },
    { name: "Bee Feed (5kg)", price: 4500 },
  ],
  services: [
    { name: "Beginner Training", price: 25000 },
    { name: "Advanced Course", price: 45000 },
  ],
  policies: true,
  permissions: true,
  discount_ceiling: 10,
};

export default function BrainPanel() {
  const { data, error } = useSWR("brain", api.getBrain, { refreshInterval: 30000 });
  const loading = data === undefined && !error;
  const brain: Record<string, any> = data ?? fallbackBrain;
  const products: Product[] = brain.products ?? [];
  const services: Product[] = brain.services ?? [];
  const policiesLoaded = brain.policies_loaded ?? brain.policies ?? false;
  const permissionsLoaded = brain.permissions_loaded ?? brain.permissions ?? false;

  return (
    <section className="panel p-7">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-[10px] uppercase tracking-[0.2em] text-[rgba(255,255,255,0.4)]">Business Brain</h2>
        <span className="text-[10px] uppercase tracking-[0.15em] text-[rgba(255,255,255,0.2)]">Updates every 30s</span>
      </div>
      {loading ? (
        <div className="grid grid-cols-2 gap-10">
          <div className="skeleton h-28" />
          <div className="skeleton h-28" />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2">
            <BrainList title={`Products (${products.length})`} values={products} className="border-r border-[rgba(255,255,255,0.05)] pr-10" />
            <BrainList title={`Services (${services.length})`} values={services} className="pl-10" />
          </div>
          <div className="mt-6 flex gap-8 border-t border-border pt-5 text-xs text-[rgba(255,255,255,0.4)]">
            <span className={policiesLoaded ? "text-green" : "text-red"}>{policiesLoaded ? "✓" : "×"} Policies</span>
            <span className={permissionsLoaded ? "text-green" : "text-red"}>{permissionsLoaded ? "✓" : "×"} Permissions</span>
            <span>Discount ceiling: {brain.discount_ceiling ?? 0}%</span>
          </div>
        </>
      )}
    </section>
  );
}

function BrainList({ title, values, className = "" }: { title: string; values: Product[]; className?: string }) {
  return (
    <div className={className}>
      <div className="section-label mb-3">{title}</div>
      {values.length ? (
        <div className="space-y-2">
          {values.map((item, i) => (
            <div key={item.id ?? i} className="flex justify-between gap-4 text-sm">
              <span className="text-primary">{item.name}</span>
              <span className="text-[rgba(255,255,255,0.4)]">{money(item.price ?? item.price_ngn)}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-secondary">No records loaded.</p>
      )}
    </div>
  );
}
