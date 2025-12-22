export default function StatCard({ title, value }) {
  return (
    <div className="border-[6px] border-black p-6 shadow-[6px_6px_0_0_black] bg-white">
      <h3 className="text-xl font-black uppercase mb-2">{title}</h3>
      <p className="text-4xl font-black text-red-600">{value}</p>
    </div>
  );
}
