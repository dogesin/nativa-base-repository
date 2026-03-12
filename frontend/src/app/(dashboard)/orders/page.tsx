import { SiteHeader } from "@/components/layout/site-header"

export default function OrdersPage() {
  return (
    <>
      <SiteHeader />
      <div className="flex flex-1 flex-col p-6">
        <h1 className="text-2xl font-semibold">Órdenes</h1>
        <p className="text-muted-foreground">Listado de órdenes (conectar con feature orders).</p>
      </div>
    </>
  )
}
