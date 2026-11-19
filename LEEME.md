# Proyecto final – De servidor vulnerable a servidor protegido

## Contenido de esta carpeta

| Ruta | Qué es |
|---|---|
| `Informe_Final_Seguridad.pdf` | Informe generado (portada, escenario, diagnóstico, controles, registros, respaldo, validación, tabla comparativa, conclusiones, anexos). |
| `evidencias/` | Las capturas renombradas con su ID (`E01…E17`, `E05b`). Copias de las originales en Descargas; los originales no se tocaron. |
| `evidencias/incidencias/` | Capturas de errores durante la práctica (`I01…I08`). Se usan en el Anexo B. |
| `evidencias/pendientes/` | **Aquí se guardan las capturas que faltan** (`P1…P10`). |
| `scripts/` | Scripts para repetir todo el laboratorio (`01…05`). |
| `GUION_SUSTENTACION.md` | Guion de 15 minutos para la sustentación (9 y 11 de nov): tiempos, quién dice qué, comandos en vivo, plan B, preguntas probables y ensayo. |
| `GUION_PARA_MEMORIZAR.md` | Una hoja con lo que hay que llevar en la cabeza: frase de arranque, tres ideas por bloque y las cifras clave. |
| `GUIA_CAPTURAS.md` | **Lo único que falta del informe:** la sesión de 30 minutos para sacar las capturas P1–P10, y los datos que hay que pasar. |
| Diapositivas | https://claude.ai/artifact/C3Tqc29qKCRQzFyjtMMb48 (18 diapositivas con el guion como notas del orador). |
| `informe/` | Fuente del informe: `plantilla.html`, `datos.json`, `estilo.css`, `diagrama_red.svg`, `build_informe.py`. |

## Qué falta para entregar

1. **Completar `informe/datos.json`**: institución, docente, segundo integrante, organización ficticia, reparto del trabajo, responsables
   y las dos incidencias (DNS y scp). Todo lo que aparece en amarillo en el PDF sale de ahí o de `plantilla.html`.
2. **Tomar las capturas `P1…P10`** (están descritas, con su comando, en cada recuadro amarillo del PDF) y guardarlas en
   `evidencias/pendientes/` empezando el nombre por su ID, por ejemplo `P2_nmap_final.png`.
   Los scripts `scripts/04_validacion_ubuntu.sh` (en Ubuntu) y `scripts/05_validacion_kali.sh` (en Kali) sacan casi todas de una vez.
3. **Regenerar el PDF**:

```powershell
cd "C:\Users\aprendiz.ti\Downloads\proyect grado\seguridad_informatica\informe"
python -I build_informe.py
```

El generador incrusta solo las capturas `P*` que existan; las demás siguen saliendo como recuadro amarillo "PENDIENTE".
Cuando no quede nada en amarillo, el PDF está listo.

## Para la carpeta de evidencias que se entrega

`evidencias/`, `scripts/` y el PDF. Si se quiere dejar limpio, `informe/` también se puede incluir (es la fuente).
