import React from "react";
import { useAuth } from "../../contexts/AuthContext";

const ComradeDashboard = () => {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    console.log("[ComradeDashboard] Logout clicked");
    logout();
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white font-sans">
      <div className="border-4 border-black p-8 shadow-lg max-w-md w-full text-center">
        <h1 className="text-3xl font-black uppercase mb-4">
          Comrade Dashboard
        </h1>

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
    </div>
  );
};

export default ComradeDashboard;
