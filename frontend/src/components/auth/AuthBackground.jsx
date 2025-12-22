export default function AuthBackground() {
  return (
    <>
      {/* Base background (color / shapes if any) */}
      <div className="absolute inset-0 bg-white" />

      {/* Halftone / shards layer */}
      <div
        className="absolute inset-0 pointer-events-none opacity-10"
        style={{
          backgroundImage:
            "radial-gradient(circle, #000000 2px, transparent 2.5px)",
          backgroundSize: "12px 12px",
        }}
      />

      {/* Accent blobs (optional, matches your vibe) */}
      <div className="absolute -top-24 -left-24 w-72 h-72 bg-[#FF0000] rounded-full opacity-10" />
      <div className="absolute bottom-0 -right-24 w-96 h-96 bg-black rounded-full opacity-5" />
    </>
  );
}
