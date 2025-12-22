export default function FeatureCard({
  title,
  description,
  icon,
  className = "",
}) {
  return (
    <div
      className={`
        group relative border-[6px] border-black bg-white p-8
        hover:bg-black hover:text-white transition-colors duration-0
        flex flex-col items-start h-full
        ${className}
      `}
    >
      {/* Icon */}
      <div className="mb-6 bg-[#FF0000] border-[4px] border-black p-4 text-white group-hover:border-white group-hover:bg-white group-hover:text-black transition-colors duration-0">
        <span className="text-3xl font-black">{icon}</span>
      </div>

      {/* Title */}
      <h3 className="text-3xl font-black uppercase mb-4 font-['Arial_Black','Arial',sans-serif] tracking-tighter">
        {title}
      </h3>

      {/* Description */}
      <p className="text-lg font-bold leading-tight">{description}</p>

      {/* Decorative block */}
      <div className="absolute bottom-4 right-4 w-4 h-4 bg-black group-hover:bg-[#FF0000]" />
    </div>
  );
}
