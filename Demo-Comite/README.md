# RutaExpress — Demo web para el comité

Interfaz en **orden del flujo operativo**: **Portal B2B (Trazabilidad) (APP-18)** → **TMS (Transportation Management) (APP-11)** → **App de Conductores (APP-15)** → **Dashboards Operativos (APP-23)**.

## Arranque local

```powershell
cd Demo-Comite
npm install
npm start
```

Abre **http://localhost:3080**

Las variables del MVP están en `lib/config.js` (no hace falta `.env`).

## Despliegue en AKS (recomendado)

```powershell
cd Demo-Comite
npm run deploy:aks
```

Publica la imagen en `acrrutaexpressmvp.azurecr.io/demo-comite` y expone un LoadBalancer.  
URL actual del despliegue: **http://52.224.204.193**

> App Service no está disponible en la suscripción (cuota VM = 0 en East US). Se usa el AKS del MVP.

## Flujo sugerido para presentar (orden de las pestañas)

1. **Portal B2B (Trazabilidad) (APP-18)** — Pedido (E1–E4). El TMS asigna ruta **en automático** (no requiere clic en esa pestaña).
2. **TMS (Transportation Management) (APP-11)** — *(Opcional)* Mostrar al comité el panel de despacho; solo clic manual para incidencia E5 en *Extra*.
3. **App de Conductores (APP-15)** — Foto y confirmación de entrega (E6–E7).
4. **Portal B2B (Trazabilidad) (APP-18)** — Rastrear envío (E8).
5. **Dashboards Operativos (APP-23)** — Indicadores (vista demo).

## Configuración

Valores fijos del MVP en `lib/config.js` (APIM, AWS ALB, Service Bus).  
Opcional: `.env` o `SERVICE_BUS_CONNECTION_STRING` en el pod para E5 sin `az login`.
