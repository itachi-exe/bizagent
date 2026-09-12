import { useState } from "react";
import Navbar from "../components/Navbar";
import UploadZone from "../components/UploadZone";
import { api, type Product } from "../api/client";
type Review = {
  upload_id: string;
  products: Product[];
  services?: Product[];
  policies?: Record<string, string>;
};
export default function UploadDatabase() {
  const [review, setReview] = useState<Review | null>(null);
  const [notice, setNotice] = useState("");
  const upload = async (file: File) => {
    const response = await api.uploadDatabase(file);
    const extracted = response.extracted ?? response;
    setReview({
      upload_id: response.upload_id ?? extracted.upload_id,
      products: extracted.products ?? [],
      services: extracted.services ?? [],
      policies: extracted.policies ?? {},
    });
  };
  const update = (index: number, field: keyof Product, value: string) =>
    setReview(
      (current) =>
        current && {
          ...current,
          products: current.products.map((p, i) =>
            i === index
              ? { ...p, [field]: field === "name" ? value : Number(value) }
              : p,
          ),
        },
    );
  const confirm = async () => {
    if (!review) return;
    try {
      await api.confirmUpload(review);
      setNotice(
        `Saved. ${review.products.length} products added to your Business Brain.`,
      );
      setReview(null);
    } catch {
      setNotice("Could not save this data. Please try again.");
    }
  };
  return (
    <main className="min-h-screen bg-[#0d0d0d]">
      <Navbar />
    <div className="mx-auto max-w-5xl px-12 py-14">
        <p className="section-label">Business brain</p>
      <h1 className="mt-3 text-4xl font-light">Upload Business Data</h1>
      <div className="mt-10">
          {notice && (
            <p
              className={`mb-5 text-sm ${notice.startsWith("Saved") ? "text-green" : "text-red"}`}
            >
              {notice}
            </p>
          )}
          {!review ? (
            <>
              <UploadZone onUpload={upload} />
              <p className="mt-4 max-w-lg text-sm text-[rgba(255,255,255,0.4)]">
                Upload your product catalogue, price list, or policy document. BizAgent will extract the information and load it into your business brain.
              </p>
              <p className="mt-3 text-center text-xs text-[rgba(255,255,255,0.2)]">
                Your data is processed securely and never shared.
              </p>
              <div className="mt-20 grid grid-cols-3 gap-12 border-t border-[rgba(255,255,255,0.05)] pt-16">
                <UploadFeature
                  number="01"
                  title="CSV & XLSX"
                  description="Spreadsheet product catalogues with prices and stock counts"
                />
                <UploadFeature
                  number="02"
                  title="PDF & DOCX"
                  description="Printed price lists, menus, and policy documents"
                />
                <UploadFeature
                  number="03"
                  title="Instant extraction"
                  description="Data is processed and ready to review in seconds"
                />
              </div>
            </>
          ) : (
            <section className="panel p-7">
              <div className="mb-6 flex justify-between">
                <div>
                  <span className="text-green">✓</span>{" "}
                  <span className="text-sm">
                    Data extracted and ready for review
                  </span>
                </div>
                <button
                  onClick={() => setReview(null)}
                  className="text-sm text-secondary hover:text-primary"
                >
                  Discard
                </button>
              </div>
              <h2 className="text-sm font-normal tracking-wide text-primary">
                Products found ({review.products.length})
              </h2>
              <table className="mt-4 w-full border-collapse text-left text-sm">
                <thead className="border-b border-[rgba(255,255,255,0.05)] text-[10px] uppercase tracking-[0.15em] text-secondary">
                  <tr>
                    <th className="py-3 font-medium">Name</th>
                    <th className="font-medium">Price (NGN)</th>
                    <th className="font-medium">Stock</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {review.products.map((product, i) => (
                    <tr key={i} className="border-b border-[rgba(255,255,255,0.05)]">
                      <td className="py-2 pr-3">
                        <input
                          value={product.name}
                          onChange={(e) => update(i, "name", e.target.value)}
                          className="input py-1.5"
                        />
                      </td>
                      <td className="pr-3">
                        <input
                          type="number"
                          value={product.price ?? product.price_ngn ?? ""}
                          onChange={(e) => update(i, "price", e.target.value)}
                          className="input py-1.5"
                        />
                      </td>
                      <td className="pr-3">
                        <input
                          type="number"
                          value={product.stock ?? ""}
                          onChange={(e) => update(i, "stock", e.target.value)}
                          className="input py-1.5"
                        />
                      </td>
                      <td>
                        <button
                          onClick={() =>
                            setReview(
                              (v) =>
                                v && {
                                  ...v,
                                  products: v.products.filter(
                                    (_, n) => n !== i,
                                  ),
                                },
                            )
                          }
                          className="text-secondary hover:text-red"
                        >
                          ×
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <button
                onClick={() =>
                  setReview(
                    (v) =>
                      v && {
                        ...v,
                        products: [
                          ...v.products,
                          { name: "", price: 0, stock: 0 },
                        ],
                      },
                  )
                }
                className="mt-4 text-sm text-green"
              >
                + Add row
              </button>
              {review.policies && Object.keys(review.policies).length > 0 && (
                <div className="mt-8 border-t border-border pt-6">
                  <h2 className="text-sm font-normal tracking-wide text-primary">Policies found</h2>
                  {Object.entries(review.policies).map(([key, value]) => (
                    <label key={key} className="mt-3 block text-sm">
                      <span className="capitalize text-secondary">{key}</span>
                      <input
                        value={value}
                        onChange={(e) =>
                          setReview(
                            (v) =>
                              v && {
                                ...v,
                                policies: {
                                  ...v.policies,
                                  [key]: e.target.value,
                                },
                              },
                          )
                        }
                        className="input mt-1"
                      />
                    </label>
                  ))}
                </div>
              )}
              <div className="mt-8 flex justify-end gap-3">
                <button
                  onClick={() => setReview(null)}
                  className="button-outline"
                >
                  Discard
                </button>
                <button onClick={confirm} className="button-primary">
                  Confirm and Save
                </button>
              </div>
            </section>
          )}
        </div>
      </div>
    </main>
  );
}

function UploadFeature({
  number,
  title,
  description,
}: {
  number: string;
  title: string;
  description: string;
}) {
  return (
    <div>
      <p className="section-label">{number}</p>
      <p className="mt-2 text-sm font-light text-[rgba(255,255,255,0.5)]">
        {title}
      </p>
      <p className="mt-2 text-xs leading-6 text-[rgba(255,255,255,0.3)]">
        {description}
      </p>
    </div>
  );
}
