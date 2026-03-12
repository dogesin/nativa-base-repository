# FastAPI — Arquitectura Escalable

## Filosofía: Domain-Driven Design + Clean Architecture

La clave para proyectos grandes es organizar el código **por dominio de negocio**, no por tipo de archivo. Esto permite que cada equipo o feature sea autónomo y que el proyecto escale sin volverse un caos.

---

## Estructura de Carpetas

```
my_project/
│
├── app/
│   ├── main.py                      # Entry point, registro de routers
│   ├── core/
│   │   ├── config.py                # Settings con pydantic-settings
│   │   ├── security.py              # JWT, hashing de contraseñas
│   │   ├── dependencies.py          # Dependencias globales (get_db, etc.)
│   │   └── exceptions.py            # Excepciones base del sistema
│   │
│   ├── db/
│   │   ├── base.py                  # Base declarativa de SQLAlchemy
│   │   ├── session.py               # Engine, SessionLocal
│   │   └── migrations/              # Alembic
│   │
│   ├── domains/                     # ← El núcleo del proyecto
│   │   ├── users/
│   │   │   ├── router.py            # Endpoints HTTP del dominio
│   │   │   ├── service.py           # Lógica de negocio
│   │   │   ├── repository.py        # Acceso a base de datos
│   │   │   ├── models.py            # Modelos SQLAlchemy
│   │   │   ├── schemas.py           # Schemas Pydantic (input/output)
│   │   │   └── dependencies.py      # Inyección de dependencias del dominio
│   │   │
│   │   ├── payments/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   │
│   │   └── products/
│   │       └── ...
│   │
│   ├── shared/
│   │   ├── utils/                   # Helpers reutilizables
│   │   ├── enums.py
│   │   └── base_repository.py       # Repo genérico base (CRUD)
│   │
│   └── infrastructure/
│       ├── stripe/                  # Cliente Stripe
│       │   ├── client.py
│       │   ├── webhooks.py
│       │   └── exceptions.py
│       ├── email/                   # Servicio de email
│       ├── storage/                 # S3, GCS
│       ├── cache/                   # Redis
│       └── queue/                   # Celery, ARQ
│
├── tests/
│   ├── unit/
│   │   └── domains/
│   └── integration/
│
├── pyproject.toml
├── .env
└── docker-compose.yml
```

---

## Las 3 Capas por Dominio

Cada dominio sigue el mismo patrón de tres capas:

```
Router → Service → Repository
  ↑          ↑          ↑
HTTP      Negocio     DB/ORM
```

- El **router** solo recibe requests y delega al service. No contiene lógica.
- El **service** contiene toda la lógica de negocio. No sabe nada de HTTP ni de SQL.
- El **repository** es el único que habla con la base de datos.

### Ejemplo completo (dominio `users`)

```python
# domains/users/repository.py
class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()


# domains/users/service.py
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def register(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise EmailAlreadyExistsError()
        hashed = hash_password(data.password)
        return self.repo.create({**data.dict(), "password": hashed})


# domains/users/router.py
@router.post("/register")
def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return service.register(data)
```

---

## Repositorio Genérico Base

Evita repetir el mismo CRUD en cada dominio. Se implementa con `Generic[ModelType]` de Python:

```python
# shared/base_repository.py
from typing import Generic, TypeVar, Type
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, data: dict) -> ModelType:
        obj = self.model(**data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, id: int, data: dict) -> ModelType | None:
        obj = self.get_by_id(id)
        if obj:
            for k, v in data.items():
                setattr(obj, k, v)
            self.db.commit()
        return obj

    def delete(self, id: int) -> bool:
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False
```

Cada repo hijo **hereda** el CRUD y solo agrega lo que es único de su dominio:

```python
# domains/products/repository.py
class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: Session):
        super().__init__(Product, db)

    # Solo lo específico de products:
    def get_by_category(self, category_id: int) -> list[Product]:
        return self.db.query(Product).filter(
            Product.category_id == category_id
        ).all()
```

---

## Sistema de Dependencias (Depends)

FastAPI usa `Depends()` para inyectar servicios, repos y la sesión de DB en los endpoints.

### Capa global (core)

```python
# core/dependencies.py
def get_db():
    db = SessionLocal()
    try:
        yield db       # yield garantiza que se cierre al terminar
    finally:
        db.close()
```

### Capa por dominio

```python
# domains/users/dependencies.py
def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)):
    return UserService(repo)
```

FastAPI resuelve automáticamente todo el árbol de dependencias. En el router solo se declara el nivel más alto:

```python
@router.get("/users/{id}")
def get_user(
    id: int,
    service: UserService = Depends(get_user_service)
):
    return service.get_by_id(id)
```

### Dependencias con autenticación

```python
# core/dependencies.py
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_jwt(token)
    user = db.query(User).get(payload["sub"])
    if not user:
        raise HTTPException(status_code=401)
    return user

# Uso en un endpoint protegido
@router.post("/orders")
def create_order(
    data: OrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service)
):
    return service.create(data, user_id=current_user.id)
```

### Ventaja para tests

Las dependencias se pueden reemplazar sin tocar código de producción:

```python
app.dependency_overrides[get_db] = lambda: test_db_session
app.dependency_overrides[get_stripe_client] = lambda: MockStripeClient()
```

---

## Módulos de Infraestructura: Ejemplo con Stripe

Stripe vive en **dos lugares** distintos porque mezcla infraestructura con negocio:

```
app/
├── domains/payments/          ← "qué" quiero hacer (lógica de negocio)
│   ├── router.py              # Endpoints: /checkout, /webhook
│   ├── service.py             # Lógica: crear orden, confirmar pago
│   ├── repository.py          # Guardar transacciones en DB
│   └── schemas.py
│
└── infrastructure/stripe/     ← "cómo" se comunica con Stripe
    ├── client.py              # stripe.PaymentIntent.create(...)
    ├── webhooks.py            # Verificar firma, parsear eventos
    └── exceptions.py          # StripeError, CardDeclinedError
```

```python
# infrastructure/stripe/client.py
class StripeClient:
    def create_payment_intent(self, amount: int, currency: str) -> dict:
        return stripe.PaymentIntent.create(amount=amount, currency=currency)


# domains/payments/service.py
class PaymentService:
    def __init__(self, repo: PaymentRepository, stripe: StripeClient):
        self.repo = repo
        self.stripe = stripe   # inyectado, no importado directo

    def checkout(self, user_id: int, amount: int):
        intent = self.stripe.create_payment_intent(amount, "usd")
        return self.repo.save_transaction(user_id, intent["id"])
```

Si mañana cambias Stripe por otro proveedor, **solo tocas `infrastructure/stripe/`**. El dominio `payments` no cambia.

### Webhooks

Los webhooks van en el **router del dominio** (son eventos de negocio), pero la verificación de firma va en `infrastructure/stripe/webhooks.py`:

```python
# domains/payments/router.py
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    event = stripe_webhooks.verify(payload, request.headers["stripe-signature"])

    if event["type"] == "payment_intent.succeeded":
        await payment_service.confirm_payment(event["data"])
```

---

## Cómo Evitar Dependencias Circulares

Las dependencias circulares ocurren cuando dos módulos se importan mutuamente. Python explota con `ImportError: cannot import name 'X'`.

```python
# ❌ Circular — orders importa users, users importa orders
from app.domains.users.service import UserService    # en orders/service.py
from app.domains.orders.service import OrderService  # en users/service.py
```

### Las 4 reglas para evitarlas

#### 1. El flujo de imports siempre va hacia abajo

Define una jerarquía y nunca la rompas:

```
core/           ← no importa de nadie
  ↓
shared/         ← solo importa de core
  ↓
infrastructure/ ← solo importa de core y shared
  ↓
domains/        ← importa de core, shared e infrastructure
  ↓
main.py         ← importa de todos
```

Si `domains/users` necesita algo de `domains/orders`, hay un problema de diseño, no de código.

#### 2. Dominios nunca se importan entre sí directamente

```python
# ❌ MAL — dominio importando otro dominio
# domains/orders/service.py
from app.domains.users.service import UserService

class OrderService:
    def create(self, user_id: int):
        user = UserService().get(user_id)  # acoplamiento directo


# ✅ BIEN — inyectar la dependencia
# domains/orders/service.py
class OrderService:
    def __init__(self, repo: OrderRepository, user_service: UserService):
        self.user_service = user_service  # recibe, no importa directamente

# domains/orders/dependencies.py  ← aquí sí puedes importar ambos
from app.domains.users.dependencies import get_user_service

def get_order_service(
    repo: OrderRepository = Depends(get_order_repository),
    user_service = Depends(get_user_service),
):
    return OrderService(repo=repo, user_service=user_service)
```

El `dependencies.py` es el **único lugar** donde dos dominios se pueden conocer.

#### 3. Comunicación entre dominios vía eventos, no imports

Cuando la relación es más suelta, usa el Event Bus:

```python
# ❌ MAL — users sabe que existe payments
# domains/users/service.py
from app.domains.payments.service import PaymentService

class UserService:
    def delete(self, user_id):
        self.repo.delete(user_id)
        PaymentService().cancel_subscriptions(user_id)  # acoplado


# ✅ BIEN — users no sabe nada de payments
# domains/users/service.py
class UserService:
    def delete(self, user_id):
        self.repo.delete(user_id)
        event_bus.publish("user.deleted", {"user_id": user_id})  # desacoplado

# domains/payments/listeners.py
event_bus.subscribe(
    "user.deleted",
    lambda e: payment_service.cancel_subscriptions(e["user_id"])
)
```

#### 4. Schemas compartidos van en shared

Si dos dominios necesitan el mismo tipo o schema:

```python
# ❌ MAL — orders importa el schema de users
from app.domains.users.schemas import UserSchema

# ✅ BIEN — schema compartido en shared
# shared/schemas/user.py
class UserBasicSchema(BaseModel):
    id: int
    email: str

# domains/orders/schemas.py
from app.shared.schemas.user import UserBasicSchema  # importa de shared, no de domains
```

### Cómo detectar circulares antes de que exploten

```bash
pip install pydeps
pydeps app --max-bacon=3 --cluster   # genera un grafo visual de dependencias
```

### El mapa de decisión

```
¿Un dominio necesita algo de otro dominio?
        ↓
¿Es para construirlo (instanciarlo)?  →  Inyéctalo en dependencies.py
¿Es para reaccionar a algo?           →  Usa Event Bus
¿Es un tipo/schema compartido?        →  Muévelo a shared/
¿Es lógica que usan ambos?            →  Muévela a shared/utils/
```

Si sigues esta decisión en cada caso, las circulares son prácticamente imposibles porque **ningún dominio sabe de la existencia de otro**.

---

## Reglas de Oro

| Regla | Por qué |
|---|---|
| Services nunca importan de otros routers | Evita dependencias circulares |
| Repositories nunca tienen lógica de negocio | Son fáciles de testear y reemplazar |
| `core/` nunca importa de `domains/` | Core es agnóstico al negocio |
| Schemas separados de models | El input/output no siempre es igual al modelo de DB |
| Un `dependencies.py` por dominio | Inyección limpia y testeable |
| Infrastructure nunca importa de domains | El flujo de dependencias es unidireccional |

---

## Resumen del Flujo Completo

```
HTTP Request
     ↓
domains/X/router.py          ← recibe y valida HTTP
     ↓
domains/X/service.py         ← lógica de negocio
     ↓                ↓
domains/X/           infrastructure/
repository.py        stripe/ email/ cache/
(tu DB)              (servicios externos)
```

---

## Preparado para Microservicios

Si en el futuro necesitas separar el proyecto en microservicios, cada carpeta de `domains/` ya está lista para convertirse en su propio servicio independiente. La migración es casi directa ya que cada dominio:

- Tiene sus propios modelos y schemas
- No depende de otros dominios directamente
- Se comunica con infraestructura a través de interfaces inyectables