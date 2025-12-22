import { Routes, Route, Navigate } from "react-router-dom";

import AdminDashboard from "./pages/Admin/AdminDashboard";
import Users from "./pages/Admin/Users";
import Verification from "./pages/Admin/Verification";
import Bookings from "./pages/Admin/Bookings";
import Revenue from "./pages/Admin/Revenue";
import Reviews from "./pages/Admin/Reviews";

export default function AdminRoutes() {
  return (
    <Routes>
      <Route index element={<AdminDashboard />} />
      <Route path="users" element={<Users />} />
      <Route path="verification" element={<Verification />} />
      <Route path="bookings" element={<Bookings />} />
      <Route path="revenue" element={<Revenue />} />
      <Route path="reviews" element={<Reviews />} />

      {/* Safety net */}
      <Route path="*" element={<Navigate to="/admin" replace />} />
    </Routes>
  );
}
