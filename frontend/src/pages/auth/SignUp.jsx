import React, { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../contexts/AuthContext.jsx";

import AuthBackground from "../../components/auth/AuthBackground.jsx";
export default function SignUp() {
  const { signup, authStatus, error } = useAuth();

  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    role: "comrade",
  });

  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSignupSubmit = async (e) => {
    e.preventDefault();
    await signup(form);
    // OTP routing is handled globally by authStatus
  };

  return (
    <main className="relative w-full min-h-screen flex items-center justify-center font-sans overflow-hidden bg-white">
      <AuthBackground />
      <div className="relative z-10 bg-white border-[6px] border-black p-12 w-full max-w-md transform -rotate-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <h1 className="text-4xl font-black uppercase mb-8 text-[#FF0000] text-center">
          Sign Up
        </h1>

        <form className="flex flex-col gap-6" onSubmit={handleSignupSubmit}>
          <input
            type="text"
            name="username"
            value={form.username}
            onChange={handleChange}
            placeholder="Username"
            className="border-[4px] border-black p-4 font-bold text-lg"
            required
          />

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

          <select
            name="role"
            value={form.role}
            onChange={handleChange}
            className="border-[4px] border-black p-4 font-bold uppercase text-lg bg-white"
          >
            <option value="comrade">Comrade</option>
            <option value="landlord">Landlord</option>
            <option value="e_service">E-Service</option>
          </select>

          <button
            type="submit"
            disabled={authStatus === "loading"}
            className={`border-[6px] border-black py-4 font-black uppercase text-xl
              ${
                authStatus === "loading"
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-[#FF0000] text-white hover:bg-black hover:text-[#FF0000]"
              }
            `}
          >
            {authStatus === "loading" ? "Signing up..." : "Sign Up"}
          </button>
        </form>

        {error && <p className="text-red-600 font-bold mt-4">{error}</p>}

        <p className="mt-6 text-center font-bold">
          Already have an account?{" "}
          <Link to="/login" className="text-[#FF0000] underline">
            Login
          </Link>
        </p>
      </div>
    </main>
  );
}
