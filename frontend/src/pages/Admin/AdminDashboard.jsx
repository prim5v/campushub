import Sidebar from "../../components/admin/Sidebar";
import Topbar from "../../components/admin/Topbar";
import StatCard from "../../components/admin/StatCard";

export default function AdminDashboard() {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />

      <main className="flex-1">
        <Topbar />

        <section className="p-8 grid grid-cols-4 gap-8">
          <StatCard title="Students" value="1,240" />
          <StatCard title="Landlords" value="312" />
          <StatCard title="Listings" value="980" />
          <StatCard title="Verified" value="641" />
        </section>
      </main>
    </div>
  );
}
