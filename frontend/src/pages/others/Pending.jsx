import React from "react";
import { useAuth } from "../../contexts/AuthContext";
import AuthBackground from "../../components/auth/AuthBackground.jsx";

export default function Pending() {
  const { user, logout } = useAuth();

  return (
    <main className="relative w-full min-h-screen flex items-center justify-center bg-white font-sans">
      {/* AuthBackground behind the content */}
      <div className="absolute inset-0 z-0">
        <AuthBackground />
      </div>

      {/* Main content on top */}
      <div className="relative z-10 bg-yellow-100 border-4 border-yellow-400 p-12 max-w-md text-center shadow-lg">
        <h1 className="text-4xl font-bold text-yellow-700 mb-6">Account Pending</h1>
        <p className="text-lg text-yellow-900 mb-6">
          Hi {user?.username || "User"}, your account is currently pending approval. Please wait for an admin to verify your account.
        </p>
        <button
          onClick={logout}
          className="bg-yellow-700 text-white py-3 px-6 font-bold uppercase text-lg border-2 border-yellow-900 hover:bg-white hover:text-yellow-700 transition-colors"
        >
          Logout
        </button>
      </div>
    </main>
  );
}
