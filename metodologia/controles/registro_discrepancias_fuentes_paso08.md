# Registro de concordancias y discrepancias entre evidencias — Paso 8

**Fecha de apertura:** 2026-07-29  
**Estado:** en construcción; no constituye todavía una tabla de resultados
finales.

## Regla metodológica

MapBiomas Perú constituye la fuente principal del estudio:

- clase 70 — Loma costera;
- clase 24 — Infraestructura urbana;
- serie anual 1985–2024;
- transiciones y mosaicos oficiales.

Landsat Collection 2 y Sentinel-2 se emplean únicamente como controles
auxiliares reproducibles. Una discrepancia espectral no se denomina
automáticamente error de MapBiomas. Se registra como concordancia, desacuerdo o
evidencia indeterminada hasta revisar persistencia, parche completo, forma,
textura, contexto y, cuando corresponda, los índices internos del módulo.

## EVAL-001

- Estrato esperado: recuperación estable `68→70`.
- Los mosaicos MapBiomas y Landsat C2 mostraron disminución del NDVI entre
  1995, 1996 y 2000.
- Lectura provisional registrada en la ficha: desacuerdo con la recuperación
  esperada, con confianza media.
- Limitación: cuatro píxeles candidatos y sensor Landsat compartido por ambas
  cadenas de procesamiento.

## EVAL-002

- Estrato esperado: conversión estable `70→24`.
- La fracción candidata dentro de la ventana de 150 × 150 m es
  aproximadamente 0.1749 ha; esta cifra no representa necesariamente el parche
  conectado completo.
- El NDVI de los mosaicos MapBiomas aumenta entre 2019 y 2020 y disminuye hacia
  2024.
- Sentinel-2 muestra el mismo sentido general: 0.0573 en 2019, 0.0627 en 2020
  y 0.0440 en 2024.
- Landsat C2 mostró un patrón distinto: disminución en 2020 y recuperación en
  2024.
- La inspección visual observó aclaramiento progresivo en color natural y
  falso color, compatible con modificación superficial, pero no suficiente
  por sí solo para demostrar infraestructura urbana.
- Decisión pendiente: medir el parche conectado completo y revisar NDBI y
  NUACI de los mosaicos oficiales antes de emitir veredicto.

## Uso posterior en el informe

El informe podrá presentar:

1. proporción de evaluaciones con concordancia entre MapBiomas y el control
   auxiliar;
2. proporción de desacuerdos e indeterminados;
3. casos donde Landsat C2 y Sentinel-2 muestran patrones diferentes;
4. limitaciones por resolución, estacionalidad y tamaño de parche;
5. recomendaciones concretas para revisar o mejorar futuras colecciones beta.

No se publicarán coordenadas ni resultados individuales derivados del dominio
KBA restringido.
