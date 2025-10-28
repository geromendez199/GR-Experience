import Link from "next/link";

import DashboardSummary from "@/components/DashboardSummary";

export default function HomePage() {
  return (
    <main>
      <h1>GR Experience</h1>
      <p>
        Plataforma integral para visualizar telemetría, analítica y estrategia en
        tiempo real de la Toyota GR Cup.
      </p>
      <DashboardSummary />
      <Link href="/replay" style={{ display: "inline-block", marginTop: "1.5rem" }}>
        Ir al replay 3D
      </Link>
    </main>
  );
}
