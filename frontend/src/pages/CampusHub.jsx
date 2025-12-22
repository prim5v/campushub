import { Link } from "react-router-dom";
import HeroSection from "../components/HeroSection";
import FeatureCard from "../components/FeatureCard";
import CTASection from "../components/CTASection";

export default function CampusHub() {
  const features = [
    {
      title: "Verified Listings",
      description:
        "Browse safe, affordable, and verified student rooms near your campus. No fake landlords. No guesswork.",
      icon: "✅",
    },
    {
      title: "Smart Filters",
      description:
        "Filter rooms by rent, distance from campus, amenities, and room type to find what actually fits you.",
      icon: "🎯",
    },
    {
      title: "Book & Reserve",
      description:
        "Book viewing appointments or reserve rooms online before wasting time visiting random places.",
      icon: "📅",
    },
    {
      title: "Student Marketplace",
      description:
        "Buy and sell furniture, electronics, and essentials directly with other students on campus.",
      icon: "🛒",
    },
  ];

  return (
    <main className="min-h-screen bg-white font-sans selection:bg-[#FF0000] selection:text-white">
      {/* ================= NAVBAR ================= */}
      <header className="w-full border-b-[6px] border-black bg-white sticky top-0 z-50">
        <div className="container mx-auto max-w-7xl flex items-center justify-between px-4 py-4">
          <div className="text-2xl md:text-3xl font-black uppercase tracking-tighter border-[4px] border-black px-3 py-1 bg-[#FF0000] text-white transform -rotate-1">
            CampusHub
          </div>

          <div className="flex items-center gap-4 font-black uppercase">
            <Link
              to="/login"
              className="px-6 py-2 border-[4px] border-black hover:bg-black hover:text-white transition-colors"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="px-6 py-2 border-[4px] border-black bg-black text-white hover:bg-[#FF0000] hover:text-black transition-colors"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* ================= HERO ================= */}
      <HeroSection />

      {/* ================= FEATURES ================= */}
      <section className="py-24 px-4 border-b-[6px] border-black bg-white relative">
        <div className="container mx-auto max-w-7xl">
          <div className="mb-16 flex flex-col md:flex-row items-start md:items-end justify-between gap-8 border-b-[6px] border-black pb-8">
            <h2 className="text-5xl md:text-7xl font-black uppercase font-['Impact','Arial_Black',sans-serif]">
              What
              <br />
              CampusHub Does
            </h2>
            <p className="text-xl font-bold max-w-md mb-2">
              CampusHub helps students find trusted off-campus housing and
              connect with landlords — fast, safe, and stress-free.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className={index % 2 === 0 ? "md:mt-12" : ""}
              >
                <FeatureCard {...feature} />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ================= VALUE STATEMENT ================= */}
      <section className="py-24 px-4 bg-black text-white border-b-[6px] border-white relative overflow-hidden">
        <div className="container mx-auto max-w-4xl relative z-10 text-center">
          <div className="border-[6px] border-white p-8 md:p-16 bg-black transform rotate-1">
            <h2 className="text-4xl md:text-6xl font-black uppercase mb-8 font-['Impact','Arial_Black',sans-serif] leading-tight">
              Built For <span className="text-[#FF0000]">Students</span>
            </h2>
            <p className="text-xl md:text-2xl font-bold leading-relaxed">
              CampusHub is a student-focused housing platform designed to eliminate
              scams, save time, and guide students to safe, verified places to live.
              It also gives landlords direct access to genuine student tenants.
            </p>
          </div>
        </div>

        <div
          className="absolute inset-0 opacity-20 pointer-events-none"
          style={{
            backgroundImage:
              "linear-gradient(45deg, #333 25%, transparent 25%, transparent 75%, #333 75%, #333), linear-gradient(45deg, #333 25%, transparent 25%, transparent 75%, #333 75%, #333)",
            backgroundPosition: "0 0, 10px 10px",
            backgroundSize: "20px 20px",
          }}
        />
      </section>

      {/* ================= CTA ================= */}
      <CTASection />

      {/* ================= FOOTER ================= */}
      <footer className="bg-white py-12 px-4 border-t-[6px] border-black">
        <div className="container mx-auto max-w-7xl flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="text-3xl font-black uppercase tracking-tighter border-[4px] border-black p-2 bg-[#FF0000] text-white transform -rotate-2">
            CampusHub
          </div>

          <div className="flex gap-8 font-bold uppercase">
            <a href="#" className="hover:bg-black hover:text-white px-2">
              Privacy
            </a>
            <a href="#" className="hover:bg-black hover:text-white px-2">
              Terms
            </a>
            <a href="#" className="hover:bg-black hover:text-white px-2">
              Contact
            </a>
          </div>

          <div className="text-sm font-bold">
            © 2024 CampusHub — Student Housing Made Simple
          </div>
        </div>
      </footer>
    </main>
  );
}
