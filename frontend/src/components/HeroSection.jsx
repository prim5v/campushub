import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function HeroSection() {
  return (
    <section className="relative w-full min-h-screen bg-white overflow-hidden border-b-[6px] border-black flex flex-col justify-center py-20">
      {/* Halftone Overlay */}
      <div
        className="absolute inset-0 pointer-events-none opacity-10 z-0"
        style={{
          backgroundImage:
            "radial-gradient(circle, #000000 2px, transparent 2.5px)",
          backgroundSize: "12px 12px",
        }}
      />

      <div className="container mx-auto px-4 relative z-10">
        <div className="max-w-7xl mx-auto">
          {/* Label */}
          <div className="absolute top-0 right-4 md:right-20 transform rotate-3 bg-black text-white px-6 py-2 border-[4px] border-[#FF0000]">
            <span className="text-xl font-black uppercase tracking-widest">
              Est. 2024
            </span>
          </div>

          {/* Headline */}
          <div className="flex flex-col items-start space-y-2 mb-12">
            <h1 className="text-[60px] md:text-[100px] leading-[0.85] font-black uppercase font-['Impact','Arial_Black',sans-serif] tracking-tighter text-black mix-blend-multiply">
              <span className="block transform -rotate-1">
                Find Your
              </span>
              <span className="block text-[#FF0000] bg-black px-4 ml-0 md:ml-12 transform rotate-1 border-[6px] border-black w-fit">
                Perfect Room
              </span>
              <span className="block transform -rotate-2 mt-2">
                with CampusHub
              </span>
            </h1>
          </div>

          {/* Subheading & CTA */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-end">
            <div className="bg-white border-[6px] border-black p-8 transform rotate-1 shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]">
              <p className="text-2xl md:text-3xl font-bold leading-tight font-['Arial_Black',sans-serif]">
                CampusHub helps students find verified, safe, and affordable housing near campus.
                <br />
                <span className="bg-[#FF0000] text-white px-1">
                  Browse, reserve, and connect
                </span>{" "}
                with landlords seamlessly.
              </p>
            </div>

            <div className="flex flex-col gap-4">
              <Link
                to="/signup"
                className="w-full bg-black text-white border-[6px] border-black p-6 text-2xl font-black uppercase hover:bg-[#FF0000] hover:text-black transition-colors duration-0 flex items-center justify-between group"
              >
                <span>Get Started</span>
                <ArrowRight className="w-8 h-8 group-hover:translate-x-2 transition-transform duration-0" />
              </Link>
              <Link
                to="/login"
                className="w-full bg-white text-black border-[6px] border-black p-6 text-2xl font-black uppercase hover:bg-black hover:text-white transition-colors duration-0 flex items-center justify-center"
              >
                Login
              </Link>

              {/* Decorative lines */}
              <div className="flex gap-4 mt-2">
                <div className="h-4 flex-grow bg-black" />
                <div className="h-4 w-4 bg-[#FF0000] border-[2px] border-black" />
                <div className="h-4 w-4 bg-black" />
                <div className="h-4 flex-grow bg-[#FF0000] border-[2px] border-black" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Badge */}
      <div className="absolute bottom-20 left-10 w-32 h-32 border-[6px] border-black rounded-full flex items-center justify-center transform -rotate-12 bg-[#FF0000] hidden md:flex">
        <span className="text-white font-black text-xl text-center leading-none">
          Verified
          <br />
          Housing
          <br />
          Only
        </span>
      </div>
    </section>
  );
}
