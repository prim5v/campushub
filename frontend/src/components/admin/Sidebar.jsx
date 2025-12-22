import { NavLink } from "react-router-dom";

import { useAuth } from "../../contexts/AuthContext.jsx";

export default function Sidebar() {

      const { user, logout } = useAuth();
    
      const handleLogout = () => {
        console.log("[AdminDashboard] Logout clicked");
        logout();
      };

  const linkClass =
    "block border-[4px] border-black px-4 py-3 font-black uppercase hover:bg-black hover:text-red-600";

  return (
    <aside className="w-64 bg-white border-r-[6px] border-black p-4 flex flex-col gap-4">
      <h2 className="text-3xl font-black uppercase text-red-600 text-center">
        CampusHub
      </h2>

      <nav className="flex flex-col gap-3 mt-6">
        <NavLink to="/admin" className={linkClass}>Dashboard</NavLink>
        <NavLink to="/admin/users" className={linkClass}>Users</NavLink>
        <NavLink to="/admin/verification" className={linkClass}>Verification</NavLink>
        <NavLink to="/admin/bookings" className={linkClass}>Bookings</NavLink>
        <NavLink to="/admin/revenue" className={linkClass}>Revenue</NavLink>
        <NavLink to="/admin/reviews" className={linkClass}>Reviews</NavLink>
        
        <div>
             <p className="mb-6 font-bold">
          Logged in as: <span className="text-red-600">{user?.username}</span>
        </p>

        <button
          onClick={handleLogout}
          className="bg-black text-white px-6 py-3 font-black uppercase border-4 border-black hover:bg-white hover:text-black transition"
        >
          Logout
        </button>
        </div>
      </nav>
    </aside>
  );
}
