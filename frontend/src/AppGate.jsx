import { useAuth } from "./contexts/AuthContext";
import Pending from "./pages/others/Pending";
import AuthBackground from "./components/auth/AuthBackground";

export default function AppGate({ children }) {
  const { authStatus, user } = useAuth();

  // Global loading overlay
  if (authStatus === "loading") {
    return (
      <div className="relative w-full min-h-screen">
        {/* Background behind everything */}
        <div className="absolute inset-0 z-0">
          <AuthBackground />
        </div>

        {/* Loader overlay */}
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/30 backdrop-blur-sm">
          <div className="w-16 h-16 border-4 border-red-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </div>
    );
  }

  // Pending users are blocked
  if (authStatus === "authenticated" && user?.status === "pending") {
    return <Pending />;
  }

  // Everything else: normal app content
  return (
    <div className="relative w-full min-h-screen">
      <div className="absolute inset-0 z-0">
        <AuthBackground />
      </div>
      <div className="relative z-10">{children}</div>
    </div>
  );
}
