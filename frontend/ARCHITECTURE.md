# ARCHITECTURE.md — Next.js
> Contexto para AI: lee esto antes de generar o modificar código.

---

## Estructura del proyecto

```
src/
├── app/                        # Solo rutas y layouts (Next.js App Router)
│   ├── (auth)/
│   │   ├── login/page.tsx
│   │   └── register/page.tsx
│   ├── (dashboard)/
│   │   ├── layout.tsx
│   │   └── orders/page.tsx
│   └── layout.tsx
│
├── features/                   # Lógica de negocio organizada por feature
│   └── X/
│       ├── components/         # Componentes exclusivos de esta feature
│       ├── hooks/              # Lógica + estado local/servidor
│       ├── services/           # Llamadas HTTP puras, sin estado
│       ├── store.ts            # Estado global Zustand (solo si aplica)
│       └── types.ts            # Tipos exclusivos de esta feature
│
├── components/                 # Componentes reutilizables (sin lógica de negocio)
│   ├── ui/                     # Átomos: Button, Input, Badge, Spinner
│   ├── forms/                  # Moléculas: TextField, SelectField
│   └── layout/                 # Organismos: Navbar, Sidebar, PageHeader
│
├── hooks/                      # Hooks globales reutilizables entre features
│   ├── useDebounce.ts
│   └── useLocalStorage.ts
│
├── lib/                        # Configuración y utilidades base
│   ├── api/
│   │   └── client.ts           # Cliente HTTP base (axios/fetch configurado)
│   └── utils/                  # Helpers puros sin estado
│
├── store/                      # Estado global compartido entre features
│   └── index.ts
│
└── types/                      # Tipos globales compartidos entre features
    ├── api.ts
    └── common.ts
```

---

## Reglas estrictas

### Dónde va cada cosa
| Qué | Dónde |
|-----|-------|
| Nueva ruta / página | `app/X/page.tsx` |
| Layout de una sección | `app/X/layout.tsx` |
| Componente exclusivo de UNA ruta | `app/X/_components/` |
| Componente exclusivo de una feature | `features/X/components/` |
| Componente reutilizable entre features | `components/ui/` o `components/forms/` |
| Lógica + fetching de datos | `features/X/hooks/useX.ts` |
| Llamada HTTP pura | `features/X/services/X.service.ts` |
| Estado global del cliente | `features/X/store.ts` o `store/index.ts` |
| Hook reutilizable sin negocio | `hooks/useX.ts` |
| Tipo exclusivo de una feature | `features/X/types.ts` |
| Tipo compartido entre features | `types/` |
| Helper puro sin estado | `lib/utils/` |
| Config del cliente HTTP | `lib/api/client.ts` |

### Lo que NUNCA debes hacer
- ❌ Poner lógica de negocio directamente en `page.tsx`
- ❌ Llamar a una API directamente desde un componente (usar hooks)
- ❌ Importar una feature desde otra feature directamente
- ❌ Importar de `features/` desde `components/ui/`
- ❌ Usar Zustand para datos que vienen del servidor (usar React Query / SWR)
- ❌ Mutar el estado de Zustand directamente sin `set()`
- ❌ Poner tipos de negocio en `components/`

---

## Flujo de imports (solo hacia abajo)

```
lib/ → types/ → components/ui/ → components/forms/ → components/layout/
                                                              ↓
                                                        features/X/
                                                              ↓
                                                        app/X/page.tsx
```

Nunca en sentido contrario.

---

## Comunicación entre features

```
# Si feature A necesita datos de feature B al renderizar:
→ Elevar el estado a store/index.ts (Zustand compartido)

# Si feature A reacciona a algo que hizo feature B:
→ Usar el store compartido como canal:
  - Feature B:  useStore.setState({ lastAction: "order.created" })
  - Feature A:  const action = useStore(s => s.lastAction)

# Si dos features comparten un tipo:
→ Moverlo a types/
```

---

## Cuándo usar cada herramienta de estado

```
¿De dónde viene el dato?
        ↓
De una API / servidor         →  React Query / SWR (en hooks/useX.ts)
Estado local de un componente →  useState / useReducer
Compartido entre features     →  Zustand (store/)
```

Distribución recomendada en proyectos grandes:
- 80% React Query (datos del servidor)
- 15% useState (estado local)
- 5% Zustand (estado global del cliente: auth, carrito, UI global)

---

## Patrón de cada feature

```typescript
// features/X/services/X.service.ts — llamadas HTTP puras, sin estado
export const xService = {
  getAll: (filters: XFilter) => apiClient.get<X[]>("/x", { params: filters }),
  getById: (id: string)      => apiClient.get<X>(`/x/${id}`),
  create: (data: CreateXDto) => apiClient.post<X>("/x", data),
}

// features/X/hooks/useX.ts — lógica + estado, llama al service
export function useX(filters: XFilter) {
  return useQuery({
    queryKey: ["x", filters],
    queryFn:  () => xService.getAll(filters),
  })
}

// features/X/components/XList.tsx — solo UI, llama al hook
export function XList() {
  const { data, isLoading } = useX({})
  if (isLoading) return <Spinner />
  return data.map(item => <XCard key={item.id} item={item} />)
}

// app/X/page.tsx — solo punto de entrada, sin lógica
export default function XPage() {
  return <XList />
}
```

---

## Server Components vs Client Components

```typescript
// Por defecto en app/ → Server Component (sin estado, sin eventos)
// app/orders/page.tsx
export default async function OrdersPage() {
  const orders = await ordersService.getAll()   // fetch directo en servidor
  return <OrderList orders={orders} />
}

// Necesita useState, onClick, hooks → agregar "use client"
// features/orders/components/OrderCard.tsx
"use client"
export function OrderCard({ order }: { order: Order }) {
  const [expanded, setExpanded] = useState(false)
  ...
}
```

Regla: **server components para fetching inicial, client components para interactividad**.

---

## Archivos especiales de Next.js (solo en app/)

| Archivo | Para qué |
|---------|----------|
| `page.tsx` | Ruta pública |
| `layout.tsx` | Layout compartido de la sección |
| `loading.tsx` | Skeleton automático mientras carga |
| `error.tsx` | Error boundary de la ruta |
| `not-found.tsx` | Página 404 de la sección |
| `route.ts` | API endpoint (Route Handler) |
| `_components/` | Componentes privados de esa ruta (el `_` los excluye de rutas) |
