import Sidebar from "../../components/admin/Sidebar";
import Topbar from "../../components/admin/Topbar";
import UserCard from "../../components/admin/UserCard";
import users from "../../data/mockUsers";

export default function Users() {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <main className="flex-1">
        <Topbar />

        <section className="p-8">
          <h1 className="text-4xl font-black uppercase mb-6">Users Database</h1>

          <div className="flex gap-4 mb-6">
            <button className="border-[4px] border-black px-4 py-2 font-black">All</button>
            <button className="border-[4px] border-black px-4 py-2 font-black">Comrade</button>
            <button className="border-[4px] border-black px-4 py-2 font-black">Landlord</button>
            <button className="border-[4px] border-black px-4 py-2 font-black">E-Service</button>
          </div>

          <div className="grid grid-cols-4 gap-6">
            {users.map(u => <UserCard key={u.id} user={u} />)}
          </div>
        </section>
      </main>
    </div>
  );
}
