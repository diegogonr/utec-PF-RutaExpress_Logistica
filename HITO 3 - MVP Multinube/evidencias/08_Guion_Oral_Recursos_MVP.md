# Guion oral — Recursos desplegados (MVP Multinube)

> Para exposiciones. Léelo en voz alta; los *entre asteriscos* son énfasis o pausas naturales.  
> Duración aproximada: **2–3 minutos**.

---

## Cómo empezar

«Voy a mostrarles muy rápido **qué desplegamos en cada nube** y **para qué sirve**, así se entiende el rol de Azure, AWS y GCP en el MVP.»

---

## Azure — el hub

«Empezamos por **Azure**, que es el **hub operativo**.  
Todo lo que montamos ahí quedó dentro de un solo contenedor: el **Resource Group `rg_Diego_Gonzales`**.  
Eso nos permite ver, administrar y, si hace falta, limpiar el ambiente demo de forma ordenada.

Dentro de ese resource group creamos, en pocas palabras, esto:

- En **AKS** corren nuestras apps principales: el orquestador de pedidos y el microservicio de inventario.  
- **ACR** guarda las imágenes de contenedor que AKS consume.  
- **API Management** es la puerta de entrada: ahí entran las APIs y también los **mocks** de WMS, ERP, TMS y portal, para no depender de los legados reales en la demo.  
- **Key Vault** guarda los secretos — por ejemplo las connection strings del bus.  
- **Azure SQL** sostiene las bases transaccionales: pedidos e inventario.  
- **Event Hubs** y **Service Bus** forman el bus de eventos: uno para streaming y el otro para colas con reintentos y DLQ.  
- **Redis** es la caché ligera.  
- Y con **Log Analytics** y **App Insights** tenemos observabilidad.

En una frase: *en Azure está el núcleo de operaciones del MVP*.»

---

## AWS — la última milla

«Pasamos a **AWS**, que en este diseño es la **última milla móvil**.

- **ECR** es el registro donde está la imagen de la API móvil.  
- Esa imagen corre en **ECS con Fargate**: aquí lo importante es que **no administramos servidores**; levantamos un task con la API y el retry worker juntos, listo para la demo.  
- Las evidencias de entrega —fotos, firmas— van a **S3**, cifradas con **KMS**, y con un lifecycle de noventa días para no acumular costo de más.  
- **DynamoDB** actúa como outbox móvil: guardamos el estado de lo pendiente de publicar, con pago on-demand y TTL, coherente con un ambiente de prueba.

En una frase: *AWS sostiene la app de campo y el puente de eventos hacia Azure*.»

---

## GCP — la lectura

«Y cerramos con **GCP**, que cumple el rol de **CQRS**: separar la escritura de la lectura.

- **Cloud Run** es el projector: consume eventos —en el MVP, ligados a Event Hubs de Azure—, escribe la proyección y puede **escalar a cero** cuando no hay tráfico, que es clave para FinOps en demo.  
- **BigQuery** guarda esa proyección de tracking —la tabla `tracking_projection`— para consultas de solo lectura, como en el escenario de seguimiento del pedido.

En una frase: *GCP no reemplaza el hub; solo nos da la vista analítica de lectura*.»

---

## Cómo cerrar

«Entonces, recapitulando: **Azure opera**, **AWS entrega en campo**, **GCP lee**.  
Con eso demostramos el flujo crítico del MVP —orden, evento, evidencia y tracking— en tres nubes, con costos acotados para un ambiente demo.»

---

## Tips rápidos (si se traban)

| Si preguntan… | Puedes responder… |
|---|---|
| ¿Por qué tres nubes? | «Cada una tiene un rol: hub, última milla y lectura. No replicamos el mismo stack tres veces.» |
| ¿Por qué Fargate y no EKS? | «En AWS solo va un servicio móvil; Fargate es el runtime mínimo. Kubernetes ya lo tenemos en AKS.» |
| ¿Por qué Cloud Run min 0? | «En demo no queremos pagar instancias ociosas; escala cuando hay eventos.» |
| ¿El RG es el producto? | «No: el resource group solo organiza; el producto son AKS, APIM, el bus y el resto.» |
