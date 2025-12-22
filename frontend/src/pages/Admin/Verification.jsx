import { useState } from "react";
import Sidebar from "../../components/admin/Sidebar";
import Topbar from "../../components/admin/Topbar";
import mockVerifications from "../../data/mockVerifications";

export default function Verification() {
  const [items, setItems] = useState(mockVerifications);
  const [selected, setSelected] = useState(null);

  const handleDecision = (id, decision) => {
    setItems(prev =>
      prev.map(item =>
        item.id === id ? { ...item, status: decision } : item
      )
    );
    setSelected(null);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />

      <main className="flex-1">
        <Topbar />

        <section className="p-8">
          <h1 className="text-4xl font-black uppercase mb-8">
            Verification Requests
          </h1>

          <div className="grid grid-cols-3 gap-6">
            {items
              .filter(i => i.status === "pending")
              .map(item => (
                <div
                  key={item.id}
                  className="border-[4px] border-black p-4 bg-white shadow-[4px_4px_0_0_black] cursor-pointer"
                  onClick={() => setSelected(item)}
                >
                  <img
                    src={item.avatar}
                    alt={item.name}
                    className="w-full h-40 object-cover border-[3px] border-black mb-3"
                  />
                  <h3 className="font-black uppercase">{item.name}</h3>
                  <p className="font-bold">{item.role}</p>
                  <p className="text-sm">{item.location}</p>
                </div>
              ))}
          </div>

          {/* DETAILS PANEL */}
          {selected && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white border-[6px] border-black p-8 w-full max-w-xl shadow-[8px_8px_0_0_black]">
                <h2 className="text-3xl font-black uppercase mb-4">
                  Inspection Checklist
                </h2>

                <ul className="mb-6 space-y-3">
                  {Object.entries(selected.checks).map(([key, value]) => (
                    <li
                      key={key}
                      className="flex justify-between border-[3px] border-black px-4 py-2 font-bold uppercase"
                    >
                      <span>{key}</span>
                      <span className={value ? "text-green-600" : "text-red-600"}>
                        {value ? "PASS" : "FAIL"}
                      </span>
                    </li>
                  ))}
                </ul>

                <div className="flex gap-4">
                  <button
                    onClick={() => handleDecision(selected.id, "approved")}
                    className="flex-1 bg-green-600 text-white border-[4px] border-black py-3 font-black uppercase hover:bg-black"
                  >
                    Approve
                  </button>

                  <button
                    onClick={() => handleDecision(selected.id, "rejected")}
                    className="flex-1 bg-red-600 text-white border-[4px] border-black py-3 font-black uppercase hover:bg-black"
                  >
                    Reject
                  </button>
                </div>

                <button
                  onClick={() => setSelected(null)}
                  className="mt-6 w-full border-[4px] border-black py-2 font-bold uppercase"
                >
                  Close
                </button>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
