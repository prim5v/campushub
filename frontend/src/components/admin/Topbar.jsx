export default function Topbar() {
  return (
    <header className="flex items-center justify-between border-b-[6px] border-black px-6 py-4 bg-white">
      {/* Search */}
      <input
        type="text"
        placeholder="Search anything..."
        className="border-[4px] border-black px-4 py-2 font-bold w-1/3"
      />

      {/* Right */}
      <div className="flex items-center gap-6">
        <button className="text-3xl font-black">🔔</button>

        <div className="flex items-center gap-3 border-[4px] border-black px-4 py-2">
          <img
            src="https://i.pravatar.cc/40"
            alt="admin"
            className="w-10 h-10 border-[3px] border-black"
          />
          <span className="font-black uppercase">Admin</span>
        </div>
      </div>
    </header>
  );
}
