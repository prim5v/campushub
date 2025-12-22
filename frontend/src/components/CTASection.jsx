import { Link } from "react-router-dom";

export default function CTASection() {
  return (
    <section className="w-full bg-[#FF0000] border-b-[6px] border-black py-24 px-4 relative overflow-hidden">
      {/* Background Noise / Texture */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage:
            "repeating-linear-gradient(45deg, #000 0, #000 2px, transparent 0, transparent 50%)",
          backgroundSize: "20px 20px",
        }}
      />

      <div className="container mx-auto relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          <h2 className="text-[48px] md:text-[96px] leading-[0.9] font-black uppercase font-['Impact','Arial_Black',sans-serif] mb-12 text-white drop-shadow-[4px_4px_0px_rgba(0,0,0,1)]">
            Ready to
            <br />
            <span className="bg-white text-black px-4 border-[6px] border-black inline-block transform -rotate-2 mt-4">
              Find Your Next Home?
            </span>
          </h2>

          <div className="flex flex-col md:flex-row justify-center gap-6 items-center">
            <Link
              to="/signup"
              className="bg-black text-white border-[6px] border-white px-12 py-6 text-2xl font-black uppercase hover:bg-white hover:text-black hover:border-black transition-colors duration-0 shadow-[8px_8px_0px_0px_rgba(255,255,255,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)]"
            >
              Get Started
            </Link>

            <Link
              to="/signup"
              className="bg-white text-black border-[6px] border-black px-12 py-6 text-2xl font-black uppercase hover:bg-black hover:text-white transition-colors duration-0"
            >
              Browse Marketplace
            </Link>
          </div>
        </div>
      </div>

      {/* Geometric Decorations */}
      <div className="absolute top-10 left-10 w-20 h-20 bg-black border-[4px] border-white transform rotate-45 hidden md:block" />
      <div className="absolute bottom-10 right-10 w-32 h-12 bg-white border-[4px] border-black transform -rotate-12 hidden md:block" />
    </section>
  );
}
