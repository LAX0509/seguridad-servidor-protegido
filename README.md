# De servidor vulnerable a servidor protegido

Proyecto final de **Seguridad Informática**: se monta a propósito un servidor Ubuntu inseguro para una organización ficticia (Café Montaña S.A.S.), se ataca desde Kali Linux, se diagnostican sus hallazgos y se aplican cinco controles hasta dejarlo protegido, con respaldo, restauración y validación final reproducibles.

> Laboratorio aislado en máquinas virtuales. Los scripts del estado vulnerable **no** deben ejecutarse en equipos reales.

## Qué se hizo

| Fase | Contenido |
|---|---|
| Estado inicial | Apache con permisos 777, firewall apagado, FTP (vsftpd) expuesto, SSH con acceso de root |
| Diagnóstico | Escaneo con `nmap` (puertos 21, 22, 80), intentos de fuerza bruta a SSH, revisión de `auth.log` |
| Controles C1–C5 | Actualizaciones (`apt upgrade`), permisos mínimos en el sitio web, SSH endurecido (`PermitRootLogin no`, `AllowUsers`, `MaxAuthTries 3`, `LoginGraceTime 30`), retiro de FTP, firewall `ufw` con política *default deny* |
| Registros | Trazabilidad de `sudo` y de accesos SSH fallidos/aceptados |
| Respaldo | Copia con `tar`, copia externa desde Kali y restauración probada |
| Validación | Mismo ataque antes/después, persistencia tras reinicio, tabla comparativa |

## Estructura

| Ruta | Qué es |
|---|---|
| `scripts/01…07` | Laboratorio completo, paso a paso (estado vulnerable, controles, respaldo, validación en Ubuntu y en Kali, página de la organización, SSH) |
| `evidencias/` | Capturas numeradas `E01…E17` e incidencias `I01…I08` |
| `informe/` | Fuente del informe (`plantilla.html`, `datos.json`, `build_informe.py`, diagrama de red) |
| `Informe_Final_Seguridad.pdf` | Informe final |
| `Sustentación – …pdf` | Diapositivas de la sustentación |

## Reproducir

```bash
# En el servidor Ubuntu (VM)
bash scripts/01_estado_inicial_vulnerable.sh
bash scripts/06_pagina_organizacion.sh
bash scripts/02_controles.sh
bash scripts/07_restringir_ssh.sh
bash scripts/03_respaldo_restauracion.sh
bash scripts/04_validacion_ubuntu.sh

# Desde Kali
bash scripts/05_validacion_kali.sh <IP_SERVIDOR> <USUARIO_ADMIN>
```

Regenerar el informe: `cd informe && python build_informe.py`.

**Herramientas:** Ubuntu Server, Kali Linux, nmap, OpenSSH, Apache, vsftpd, ufw, tar/scp, Python (generador del informe).

Autor: Juan Camilo Nieto Arboleda.
