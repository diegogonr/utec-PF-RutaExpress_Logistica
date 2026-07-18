# FinOps — MVP Multinube
## RutaExpress Fulfillment & Transporte

> **FinOps** (gestión financiera de la nube): visibilidad, atribución y control del gasto cloud del ambiente demo.  
> **Presupuesto objetivo MVP:** **~USD 449/mes** (ambiente único `mvp`).

---

## 1. Objetivo FinOps del MVP

| Objetivo | Cómo se cumple en el diseño |
|---|---|
| **Presupuesto predecible** | SKUs acotados (Developer, Basic C0, 1 TU, Fargate 0.25 vCPU, Cloud Run min 0) |
| **Atribución por nube y rol** | Tags/labels obligatorios + desglose Azure / AWS / GCP |
| **Evitar sorpresas** | Variables de costo controlado (`eventhub_throughput_units=1`, `aks_node_count=2`) |
| **Gate de gobernanza** | Pipeline: plan → policy check de tags → aprobación manual antes de `apply` |
| **Separar demo vs producción** | APIM Developer (~USD 50) vs Standard (~USD 700); sin SLA prod en demo académica |

---

## 2. Supuestos de costeo

| Supuesto | Valor |
|---|---|
| Ambiente | Único: `mvp` (dev/demo) |
| Tráfico | Bajo (~500 órdenes/día de prueba) |
| Horas / mes | 730 h |
| Región | US-East (`eastus` / `us-east-1` / `us-east1`) — co-localización para reducir latencia y egress |
| Soporte | Sin soporte enterprise |
| Precios | Orientativos **USD/mes**, calculadora pública (referencia julio 2026) |
| Fuera de alcance | Licencias SaaS mock externas; VPN a on premises |

---

## 3. Tags y labels obligatorios

Todos los recursos Terraform deben llevar tags (Azure/AWS) o labels (GCP) FinOps:

| Clave | Valor MVP | Uso |
|---|---|---|
| `project` | `rutaexpress` | Agrupar gasto del producto |
| `environment` | `mvp` | Separar demo de futuros `dev`/`prod` |
| `cost-center` | `logistics` | Centro de costo académico / negocio |
| `managed-by` | `terraform` | Origen IaC (PLT-04) |
| `package` | `rutaexpress-mvp` | Paquete Hito 3 (naming module) |

**Variable IaC:** `environment = mvp` alimenta estos tags.

**Gate CI/CD:** el stage `plan` exige *policy check tags* antes de merge/apply.

---

## 4. Palancas de costo en variables MVP

| Variable | Valor demo | Efecto FinOps |
|---|---|---|
| `eventhub_throughput_units` | `1` | Throughput (volumen de mensajes) mínimo — costo Event Hubs controlado |
| `aks_node_count` | `2` | MVP sin HA multi-AZ completo; cómputo AKS acotado |
| `apim_sku` | `Developer` / `Developer_1` | ~USD 50/mes vs ~700 Standard; sin SLA prod |
| `aks_vm_size` | Standard_D2s_v5 | Nodo tamaño intermedio demo |
| Regiones alineadas | eastus / us-east-1 / us-east1 | Menor latencia y egress inter-nube |

---

## 5. Desglose de costos por nube

### 5.1 Azure — hub operativo (~65 %)

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| AKS (2 nodos D2s_v5) | 2 × ~$70 | **140** |
| Azure SQL S1 | 20 DTU | **30** |
| API Management (APP-01) | Developer¹ | **50** |
| Event Hubs Standard | 1 TU + ingress bajo | **25** |
| Service Bus Standard | 1M ops | **10** |
| Redis Basic C0 | 250 MB | **16** |
| Key Vault | ~10k ops | **5** |
| Log Analytics + App Insights | 5 GB ingest | **15** |
| Storage (estado TF + audit) | 50 GB | **5** |
| **Subtotal Azure** | | **~296** |

¹ Developer no tiene SLA de producción; adecuado para demo académica. Producción: Standard ~**USD 700/mes**.

**Justificación del peso:** Azure concentra OMS/APIM, bus (Event Hubs + Service Bus), datos OLTP (SQL/Redis) y observabilidad — mayor % del total es coherente con el rol de **hub**.

### 5.2 AWS — última milla (~21 %)

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| ECS Fargate | 0.25 vCPU / 512 MB 24/7 | **38** |
| DynamoDB on-demand | 1M R/W bajo | **15** |
| S3 + KMS | 50 GB, 10k PUT | **8** |
| SQS + EventBridge | 1M requests | **5** |
| CloudWatch + X-Ray | 5 GB logs | **12** |
| Data transfer → Azure | 20 GB egress | **18** |
| **Subtotal AWS** | | **~93** |

**Nota egress:** el costo de transferencia AWS→Azure (~USD 18) es el precio de **no migrar** de golpe la última milla; mitigación MVP: eventos compactos, batching, región coherente.

### 5.3 GCP — analítica / CQRS (~14 %)

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| Cloud Run | min 0, ~50k req + push Event Hubs | **25** |
| BigQuery | 100 GB storage + queries | **25** |
| Secret Manager | 5 secretos | **2** |
| Cloud Logging | 5 GB | **8** |
| **Subtotal GCP** | | **~60** |

**Justificación:** lectura CQRS (proyección tracking E8); `min_instance_count = 0` escala a cero fuera de demo.

---

## 6. Resumen ejecutivo FinOps

| Nube | USD/mes MVP | % del total | Rol arquitectónico |
|---|---:|---:|---|
| **Azure** | ~296 | **65%** | Hub operativo (mayor peso justificado) |
| **AWS** | ~93 | **21%** | Última milla móvil |
| **GCP** | ~60 | **14%** | Analítica / CQRS (escritura vs lectura) |
| **TOTAL** | **~449** | **100%** | Ambiente demo único |

```text
Azure ████████████████████████████████  ~296 (65%)
AWS   ██████████                        ~93  (21%)
GCP   ███████                           ~60  (14%)
                                    TOTAL ~449 USD/mes
```

---

## 7. Escenarios de escala (fuera del presupuesto demo)

| Escenario | Cambio principal | USD/mes estimado |
|---|---|---|
| **Demo actual** | 500 órdenes/día, 1 TU, 2 nodos AKS | **~449** |
| **Campaña ~180k órdenes/día** | ~3–5× Event Hubs TU + más nodos AKS | **~$1,200–1,800** |

Alineado parcialmente a la escala INI-02 del Hito 1; **no** está incluido en el presupuesto del MVP demo.

---

## 8. Controles FinOps en el ciclo de vida IaC

| Momento | Control |
|---|---|
| **Diseño** | SKUs MVP explícitos en módulos Terraform |
| **PR** | `terraform plan` + comentario de coste estimado |
| **Plan** | Policy check de tags FinOps; evitar destroy accidental |
| **Apply** | Aprobación manual (arquitecto) en ambiente `mvp` |
| **Runtime** | Cloud Run min 0; S3 lifecycle 90 días; DynamoDB on-demand; Event Hubs 1 TU |
| **Tear-down** | `terraform destroy` del ambiente demo al cerrar la ventana académica |

---

## 9. Decisiones de SKU con impacto FinOps (rápido)

| Decisión | Opción MVP | Alternativa más cara | Motivo FinOps |
|---|---|---|---|
| APIM | Developer | Standard ~$700/mes | Demo sin SLA |
| Redis | Basic C0 | Standard/Premium | Caché ligera demo |
| Event Hubs | 1 TU Standard | Multi-TU | Throughput controlado |
| ECS | Fargate 0.25/512 | EKS (+ control plane) | Un solo servicio móvil |
| Cloud Run | min 0 | min ≥1 | Pagar solo con tráfico |
| DynamoDB | On-demand | Provisioned | Tráfico demo irregular |
| S3 evidencias | Lifecycle 90d | Retención indefinida | Tope de almacenamiento |

---

## 10. Checklist de aceptación FinOps (comité)

- [ ] Presupuesto **~USD 449/mes** aceptado para ambiente demo único
- [ ] Reparto 65% / 21% / 14% (Azure / AWS / GCP) entendido y justificado por rol
- [ ] Tags FinOps obligatorios confirmados en IaC
- [ ] APIM Developer aceptado solo para MVP académico (no producción)
- [ ] Egress inter-nube (~USD 18 AWS) aceptado como costo del puente
- [ ] Escala campaña ($1,200–1,800) **fuera** del alcance de costo del MVP v1
- [ ] Apply con aprobación manual y destroy al finalizar demo

---

## Referencias

| Documento | Uso |
|---|---|
| `04_IaC_Costos_Despliegue.md` | Fuente de costos, SKUs e IaC |
| `00_INDICE_COMITE.md` | Glosario e índice del paquete Hito 3 |
| `06_Preguntas_Argumentos_Comite.md` | Comparativas de arquitectura (Fargate vs Lambda, ECS vs EKS, etc.) |
