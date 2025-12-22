import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

import CampusHub from "./pages/CampusHub";
import Login from "./pages/auth/Login";
import SignUp from "./pages/auth/SignUp";
import OtpVerification from "./pages/auth/OtpVerification";

import { AuthProvider, useAuth } from "./contexts/AuthContext";
import AppGate from "./AppGate";
import RoleRouter from "./RoleRouter";

function AppRoutes() {
  const { authStatus } = useAuth();

  // AUTHENTICATED USERS → ROLE DASHBOARD
  if (authStatus === "authenticated") {
    return (
      <Routes>
        <Route path="/*" element={<RoleRouter />} />
      </Routes>
    );
  }

  // OTP FLOW
  if (authStatus === "otp_required") {
    return (
      <Routes>
        <Route path="*" element={<OtpVerification />} />
      </Routes>
    );
  }

  // PUBLIC ROUTES
  return (
    <Routes>
      <Route path="/" element={<CampusHub />} />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignUp />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
        <AppGate>
          <AppRoutes />
        </AppGate>
    </AuthProvider>
  );
}
