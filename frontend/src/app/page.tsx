import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Page() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center gap-8 p-6">
      <div className="flex max-w-md flex-col gap-4 text-center">
        <h1 className="text-2xl font-semibold">Bienvenido</h1>
        <p className="text-muted-foreground">
          Inicia sesión, regístrate o entra al dashboard.
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          <Button asChild>
            <Link href="/login">Iniciar sesión</Link>
          </Button>
          <Button variant="outline" asChild>
            <Link href="/register">Registrarse</Link>
          </Button>
          <Button variant="secondary" asChild>
            <Link href="/dashboard">Dashboard</Link>
          </Button>
        </div>
      </div>
    </div>
  )
}
