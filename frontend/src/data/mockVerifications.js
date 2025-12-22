const verifications = [
  {
    id: 1,
    name: "Peter Mwangi",
    role: "Landlord",
    location: "Near Main Campus Gate",
    avatar: "https://i.pravatar.cc/300?img=15",
    checks: {
      security: true,
      cleanliness: true,
      water: true,
      electricity: true,
      environment: false,
    },
    status: "pending",
  },
  {
    id: 2,
    name: "Grace Achieng",
    role: "E-Service",
    location: "Phase 2, Block C",
    avatar: "https://i.pravatar.cc/300?img=28",
    checks: {
      security: true,
      cleanliness: true,
      water: true,
      electricity: true,
      environment: true,
    },
    status: "pending",
  },
];

export default verifications;
