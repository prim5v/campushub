import React, { useEffect, useState } from "react";
import { useAuth } from "../../contexts/AuthContext";
import AuthBackground from "../../components/auth/AuthBackground.jsx";

export default function OtpVerification() {
  const {
    verifyOtp,
    signup,          // used for resend
    logout,
    authStatus,
    error,
    pendingEmail,
    signupPayload,   // 👈 MUST exist in AuthContext
  } = useAuth();

  const [otp, setOtp] = useState("");
  const [resendTimer, setResendTimer] = useState(60);
  const [canResend, setCanResend] = useState(false);

  /* =========================
     RESEND TIMER
  ========================= */
  useEffect(() => {
    if (resendTimer <= 0) {
      setCanResend(true);
      return;
    }

    const interval = setInterval(() => {
      setResendTimer((t) => t - 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [resendTimer]);

  if (!pendingEmail) {
    return null;
  }

  const handleVerify = async (e) => {
    e.preventDefault();
    await verifyOtp({ otp });
  };

  const handleResend = async () => {
    if (!signupPayload) {
      console.error("[OTP] Missing signup payload — cannot resend");
      return;
    }

    console.log("[OTP] Resending OTP…");
    setResendTimer(60);
    setCanResend(false);

    await signup(signupPayload);
  };

  const handleCancel = () => {
    console.log("[OTP] Cancel signup");
    logout();
  };

  return (
    <main className="relative w-full min-h-screen flex items-center justify-center font-sans overflow-hidden bg-white">
      <AuthBackground />

      <div className="absolute inset-0 bg-[radial-gradient(#000_1px,transparent_1px)] [background-size:16px_16px] opacity-10" />

      <div className="relative z-10 bg-white border-[6px] border-black p-12 w-full max-w-md shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
        <h1 className="text-4xl font-black uppercase mb-6 text-[#FF0000] text-center">
          Verify OTP
        </h1>

        <p className="text-center font-bold mb-2">
          Code sent to <span className="text-[#FF0000]">{pendingEmail}</span>
        </p>

        <p className="text-center text-sm font-bold mb-6 text-gray-700">
          OTP will expire after <span className="text-black">5 minutes</span>
        </p>

        <form className="flex flex-col gap-6" onSubmit={handleVerify}>
          <input
            type="text"
            value={otp}
            onChange={(e) => setOtp(e.target.value)}
            placeholder="Enter OTP"
            className="border-[4px] border-black p-4 font-bold text-lg"
            required
          />

          <button
            type="submit"
            className="bg-[#FF0000] text-white border-[6px] border-black py-4 font-black uppercase text-xl hover:bg-black hover:text-[#FF0000]"
          >
            {authStatus === "loading" ? "Verifying..." : "Verify OTP"}
          </button>
        </form>

        {/* ACTIONS */}
        <div className="flex justify-between items-center mt-6">
          <button
            onClick={handleCancel}
            className="font-black uppercase underline text-black hover:text-[#FF0000]"
          >
            Cancel
          </button>

          <button
            onClick={handleResend}
            disabled={!canResend}
            className={`font-black uppercase ${
              canResend
                ? "text-[#FF0000] hover:underline"
                : "text-gray-400 cursor-not-allowed"
            }`}
          >
            {canResend ? "Resend OTP" : `Resend in ${resendTimer}s`}
          </button>
        </div>

        {error && (
          <p className="text-red-600 font-bold mt-6 text-center">{error}</p>
        )}
      </div>
    </main>
  );
}
