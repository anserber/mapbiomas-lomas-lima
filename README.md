# ¿Qué puede y qué no puede decir una clase beta?

Código, datos y documentos de control del diagnóstico de la **clase 70 — Loma
costera** de MapBiomas Perú, Colección 3, sobre el **ACR Sistema de Lomas de
Lima** y su periferia externa, 1985–2024.

Este repositorio acompaña al trabajo presentado al Premio MapBiomas Perú,
tercera edición, categoría Joven.

---

## Qué contiene

```
codigo/gee/          42 scripts de Google Earth Engine
codigo/python/       31 scripts de Python
datos/               tabla maestra de las ocho unidades públicas y su diccionario
metodologia/         metodología congelada v1.0, adenda v1.1 y 32 documentos de control
```

**`datos/tabla_maestra_resultados_publicos_v2.csv`** es la fuente única de todas
las cifras publicadas: ocho unidades —cinco ámbitos del ACR y tres anillos de
periferia externa— con 28 campos. Su diccionario define cada campo, su unidad, su
procedencia y su regla de uso.

**`datos/SHA256SUMS.txt`** registra la firma de los archivos de datos, de modo
que cualquier alteración posterior sea detectable.

## Cómo reproducir el análisis

1. Revisar `metodologia/metodologia_final_lomas_mapbiomas.md` y su adenda v1.1.
2. Ejecutar los scripts de `codigo/gee/` en el orden que indica su numeración de
   paso. Requieren una cuenta de Google Earth Engine y los assets de límites,
   cuya construcción está documentada en los pasos 1 a 3.
3. Descargar los CSV resultantes y verificar sus firmas contra `SHA256SUMS.txt`.
4. Ejecutar los scripts de `codigo/python/` sobre esos CSV.

Cada script de figura declara en su cabecera el contrato de comunicación del
producto que genera: pregunta, mensaje, fuente, unidades, qué incluye, qué
excluye y qué prohíbe. Los scripts incorporan **aserciones de control** que
comparan sus totales contra la tabla maestra y detienen la ejecución si no
coinciden.

## Qué NO contiene, y por qué

**Nada relativo a la KBA Lomas de Atocongo.** Las condiciones de uso y
redistribución con que la KBA Partnership entrega el dato lo impiden. Quedan
fuera el archivo espacial original, el polígono de intersección con el ACR y los
resultados desagregados de ese ámbito.

**Esa exclusión no procede de las licencias de este repositorio** y se mantendría
aunque adoptáramos una licencia más permisiva. Afecta a un ámbito de los nueve
analizados; los ocho restantes se publican íntegros.

Algunos scripts conservan referencias a rutas locales del material restringido.
Son rutas, no datos: los archivos a los que apuntan no forman parte de este
repositorio.

**Tampoco se redistribuyen geometrías ni rásteres.** Los límites del ACR proceden
del geoservicio oficial y los productos de MapBiomas de su plataforma; ambos se
obtienen en su fuente, que es donde deben citarse.

## Fuentes de datos

Los datos de MapBiomas son públicos y abiertos bajo licencia Creative Commons
CC BY. Sus términos de uso exigen referenciar la fuente en un formato literal,
que se reproduce aquí:

> MapBiomas – Colección 3 de la Serie anual de Mapas de Cobertura y Uso del Suelo
> de Perú, consultada el 27 de julio de 2026 a través del enlace:
> https://plataforma.peru.mapbiomas.org/

Límites del ACR: Decreto Supremo N.º 011-2019-MINAM, a través del geoservicio de
SERNANP. Máscara terrestre y límites departamentales: INEI, 2023. Relieve:
NASADEM 30 m, NASA/USGS.

**Este trabajo es un uso independiente de datos públicos y no constituye un
producto institucional de MapBiomas Perú ni cuenta con su aval.**

## Licencias

| Contenido | Licencia |
|---|---|
| `codigo/` | MIT — ver `LICENSE` |
| `datos/` y `metodologia/` | Creative Commons Atribución 4.0 Internacional (CC BY 4.0) |

## Cómo citar

Usa el DOI de concepto de Zenodo, que resuelve siempre a la versión más reciente.
La cita formal está en `CITATION.cff` y GitHub la ofrece en el botón *Cite this
repository*.

## Una advertencia sobre el alcance

Los resultados describen **el comportamiento de una clase cartográfica en fase
beta** sobre un territorio delimitado. No describen condición ecológica, calidad
de hábitat ni efectividad de conservación. Una variación de superficie de una
clase binaria no es medición de cambio ecológico mientras no se descuente la
componente de conmutación del clasificador.
