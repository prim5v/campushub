export default function UserCard({ user }) {
  return (
    <div className="border-[4px] border-black p-4 shadow-[4px_4px_0_0_black] bg-white">
      <img
        src={user.avatar}
        alt={user.name}
        className="w-full h-40 object-cover border-[3px] border-black mb-3"
      />
      <h3 className="font-black uppercase">{user.name}</h3>
      <p className="font-bold">{user.role}</p>
      <p className="text-sm">{user.email}</p>
    </div>
  );
}
