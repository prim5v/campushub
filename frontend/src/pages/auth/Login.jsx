import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthBackground from "../../components/auth/AuthBackground.jsx";
import { useAuth } from "../../contexts/AuthContext.jsx"; // adjust path if needed

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const { login, authStatus, error } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const success = await login(form);
    if (success) {
      // navigate("/dashboard"); // or wherever you want to redirect after login
    }
  };

  return (
    <main className="relative w-full min-h-screen flex items-center justify-center font-sans overflow-hidden bg-white">
      <AuthBackground />

      {/* Halftone background overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-10 z-0"
        style={{
          backgroundImage: "radial-gradient(circle, #000000 2px, transparent 2.5px)",
          backgroundSize: "12px 12px",
        }}
      />

      <div className="relative z-10 bg-white border-[6px] border-black p-12 w-full max-w-md transform rotate-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <h1 className="text-4xl font-black uppercase mb-8 text-[#FF0000] text-center font-['Impact','Arial_Black',sans-serif]">
          Login
        </h1>
        <form className="flex flex-col gap-6" onSubmit={handleSubmit}>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            placeholder="Email"
            className="border-[4px] border-black p-4 font-bold text-lg"
            required
          />
          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              name="password"
              value={form.password}
              onChange={handleChange}
              placeholder="Password"
              className="border-[4px] border-black p-4 font-bold text-lg w-full"
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-sm font-bold text-[#FF0000]"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>

          <button
            type="submit"
            disabled={authStatus === "loading"}
            className={`${
              authStatus === "loading"
                ? "bg-gray-400 border-gray-600 cursor-not-allowed"
                : "bg-[#FF0000] border-black hover:bg-black hover:text-[#FF0000]"
            } text-white border-[6px] py-4 font-black uppercase text-xl transition-colors duration-0`}
          >
            {authStatus === "loading" ? "Logging in..." : "Login"}
          </button>

          {error && <p className="text-red-600 font-bold text-center">{error}</p>}
        </form>
        <p className="mt-6 text-center font-bold">
          Don't have an account?{" "}
          <Link to="/signup" className="text-[#FF0000] underline">
            Sign Up
          </Link>
        </p>
      </div>
    </main>
  );
}
