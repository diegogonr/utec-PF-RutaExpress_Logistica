# -*- coding: utf-8 -*-
"""Copia las PNG C4 del paquete MVP a Hito 2 diagramas_c4 (Alternativa A)."""
from pathlib import Path

REPO = Path(__file__).resolve().parent
h3 = next(p for p in REPO.iterdir() if p.is_dir() and p.name.startswith("HITO 3"))
h2 = next(p for p in REPO.iterdir() if p.is_dir() and p.name.startswith("HITO 2"))
src = h3 / "diagramas_c4" / "imagenes"
dst = h2 / "ARQUITECTURA_SOLUCION_TO_BE" / "diagramas_c4"

mapping = {
    "mvp_c4_n1_contexto_v4.png": "alternativa_A_n1_contexto.png",
    "mvp_c4_n2_contenedores_v20.png": "alternativa_A_n2_contenedores.png",
    "mvp_c4_n3_plt03_componentes.png": "alternativa_A_n3_componentes.png",
    "mvp_c4_n3_oms_componentes.png": "alternativa_A_n3_oms_componentes.png",
    "mvp_c4_n3_inventario_componentes.png": "alternativa_A_n3_inventario_componentes.png",
    "mvp_c4_n3_mobile_componentes.png": "alternativa_A_n3_mobile_componentes.png",
}

for sname, dname in mapping.items():
    out = dst / dname
    out.write_bytes((src / sname).read_bytes())
    print("OK", dname, len(str(out)), out.stat().st_size)
