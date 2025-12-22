import { Navigate, Routes, Route } from "react-router-dom";
import { useAuth } from "./contexts/AuthContext";

import AdminRoutes from "./AdminRoutes";
import LandlordDashboard from "./pages/LandLord/LandlordDashboard";
import ComradeDashboard from "./pages/Comrade/ComradeDashboard";
import E_serviceDashboard from "./pages/E_service/E_serviceDashboard";

export default function RoleRouter() {
  const { user } = useAuth();

  if (!user) return <Navigate to="/login" replace />;

  switch (user.role) {
    case "admin":
      return (
        <Routes>
          <Route path="/admin/*" element={<AdminRoutes />} />
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
      );

    case "landlord":
      return <LandlordDashboard />;

    case "comrade":
      return <ComradeDashboard />;

    case "e_service":
      return <E_serviceDashboard />;

    default:
      return <Navigate to="/" replace />;
  }
}
