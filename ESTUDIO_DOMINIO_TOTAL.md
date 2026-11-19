# Estudio para dominar el tema al 100 %

Para Juan Diego (y para Juan Camilo). Orden recomendado: **1)** leer esta hoja, **2)** el informe PDF, **3)** las diapositivas con sus notas, **4)** `GUION_PARA_MEMORIZAR.md`, **5)** ensayar con `GUION_SUSTENTACION.md`, **6)** autoevaluarse con la sección 5 de esta hoja.

Diapositivas: https://claude.ai/artifact/C3Tqc29qKCRQzFyjtMMb48 (cada una tiene el guion en las notas del orador).

> El docente evalúa **dominio individual** (15 %): cualquiera de los dos puede ser preguntado por cualquier parte. Quien no manejó el teclado debe explicar igual.

---

## 1. La historia en 60 segundos

Un servidor web Ubuntu (192.168.56.101) se dejó **a propósito** con cinco debilidades. Desde Kali (192.168.56.102) se diagnosticó con Nmap y se entró como root. Luego se aplicaron cinco controles, uno por debilidad, y se comprobó que el sitio y la administración legítima siguen funcionando. Se revisaron los registros, se hizo un respaldo con copia fuera de la VM y se restauró un archivo. No se busca un servidor invulnerable, sino uno **funcional, justificado y con limitaciones reconocidas**.

## 2. Las cinco debilidades y sus controles (memoricen la tabla)

| Hallazgo | Categoría | Cómo se creó | Riesgo | Control | Cómo se prueba |
|---|---|---|---|---|---|
| **H1** Root por SSH | Acceso | `PermitRootLogin yes` | Quien adivine la clave controla todo | **C3** `PermitRootLogin no` + `systemctl restart ssh` | `ssh root@…` → Permission denied; `sudo sshd -T \| grep permitrootlogin` → `no` |
| **H2** Permisos 777 | Permisos | `chmod -R 777 /var/www/html` | Cualquiera modifica o borra el sitio | **C4** `chown -R www-data:www-data` + `chmod -R 755` | `ls -ld /var/www/html`; `touch` como `juan` → denegado |
| **H3** Firewall apagado | Red | `ufw disable` | Todo servicio queda expuesto | **C5** `deny incoming`, `allow outgoing`, `allow 22/tcp`, `allow 80/tcp`, `enable` | `ufw status verbose`; Nmap solo ve 22 y 80 |
| **H4** FTP (vsftpd) | Servicio innecesario | `apt install vsftpd` | Más superficie; FTP viaja sin cifrar | **C2** `systemctl stop` + `disable vsftpd` | `systemctl is-active vsftpd` → inactive; 21 filtrado |
| **H5** Sin actualizar | Mantenimiento | no se hizo `apt upgrade` | Fallos conocidos sin corregir | **C1** `apt update && apt upgrade -y` | `apt list --upgradable`; kernel 7.0.0-42 |

Prioridad: **alta** H1, H2, H3, H5 (dan control, modifican el sitio o dejan todo sin defensa); **media** H4.

## 3. Conceptos que hay que poder explicar con sus palabras

- **Puerto abierto ≠ vulnerabilidad.** Importa si el servicio es necesario y cómo está configurado. 22 (SSH) y 80 (HTTP) son legítimos; el 21 sobra.
- **Nmap `-sV -p-`:** `-sV` detecta versiones; `-p-` recorre los 65 535 puertos. *closed* = el sistema responde con reinicio (sin firewall); *filtered* = el firewall descarta el paquete y Nmap no recibe respuesta. Por eso, con UFW, `-p-` tarda: en vivo se escanean solo 21, 22 y 80.
- **Por qué no root por SSH:** es la cuenta más conocida y atacada. Con usuario normal + `sudo` hay **trazabilidad**: queda registrado quién hizo qué.
- **`sshd -T`:** muestra la configuración **efectiva**, la que el servidor aplica. Es la prueba concluyente: en el registro, un intento de root rechazado puede verse igual que una clave equivocada.
- **Permisos rwx:** tres juegos —dueño, grupo, otros—. 777 = `rwx rwx rwx`; 755 = `rwx r-x r-x` (4 leer, 2 escribir, 1 ejecutar). `www-data` es el usuario con que corre Apache: dueño legítimo del sitio.
- **UFW:** `deny incoming` bloquea lo que llega; `allow outgoing` deja salir (actualizaciones, respuestas). Las reglas 22 y 80 van **antes** de `enable` para no perder la sesión SSH. `ufw enable` es persistente: arranca con el sistema.
- **`stop` vs `disable`:** `stop` cierra el puerto ahora; `disable` evita que arranque al reiniciar. El paquete se deja para poder revertir en el laboratorio.
- **Registros:** `/var/log/auth.log`; cada línea trae evento, usuario e **IP de origen**; la hora está en **UTC** (Colombia = UTC−5: 00:49 UTC = 19:49). `grep -a` porque el archivo contiene caracteres no imprimibles. Los `sudo` también quedan (E13).
- **Respaldo:** `tar -czvf` (crear, comprimir, listar) del sitio y las configuraciones críticas. **Copia fuera de la VM** con `scp` a Kali, y `sha256sum` para verificarla: una copia en la misma máquina se pierde con ella.
- **Restauración:** `tar -xzvf … -C /` extrae en las rutas originales (tar guarda las rutas sin la `/` inicial). Para un solo archivo: `… -C / var/www/html/index.html`. Como root conserva dueño y permisos. **El respaldo debe ser posterior a los controles**; uno del estado vulnerable devolvería `PermitRootLogin yes` y 777.
- **Instantánea de VirtualBox:** conserva el estado inicial vulnerable (E05) para poder comparar antes/después.
- **Red solo-anfitrión:** las dos VM se ven entre sí (192.168.56.0/24) y no tienen Internet; cumple la regla de red aislada.

## 4. Lo que el docente puede atacar (preparen la respuesta honesta)

| Punto débil | Respuesta |
|---|---|
| Archivos en 755 y no 644 | Se aplicó 755 recursivo por simplicidad; lo más fino es 755 directorios y 644 archivos. Está como mejora pendiente. |
| SSH sigue aceptando contraseñas | Es riesgo pendiente: llaves, `AllowUsers juan`, `MaxAuthTries`, `fail2ban`/`ufw limit 22/tcp`, limitar origen. |
| HTTP sin cifrar | Pendiente: TLS (autofirmado en laboratorio). |
| Ubuntu con escritorio y no Server | Declarado como limitación; los controles son los mismos. |
| Respaldo manual | Pendiente: `cron`, cifrado con `gpg`, varias copias; se incluyó `user.rules` y `user6.rules` porque `ufw.conf` no guarda las reglas. |
| Se dio Internet temporal para `apt upgrade` | Fue la única excepción al aislamiento y se explica en el informe (incidencia I03). |
| Los 8 errores del Anexo B | Se mostraron como aprendizaje: rutas con espacios, `-c` vs `-C`, `grep -a`, DNS, IP por DHCP. |

## 5. Autoevaluación (respondan sin mirar)

1. ¿Cuáles son las cinco debilidades y su categoría?
2. ¿Por qué el 22 y el 80 abiertos no son hallazgos?
3. ¿Cómo demuestran que root está bloqueado y no que la clave estaba mal?
4. ¿Qué significa 755? ¿Y 777? ¿Quién es `www-data`?
5. ¿Por qué `allow 22` antes de `enable`?
6. Diferencia entre `deny incoming` y `allow outgoing`.
7. Diferencia entre `stop` y `disable`.
8. ¿Qué es *filtered* y por qué aparece el 21 así ahora?
9. ¿Dónde están los registros? ¿En qué hora? ¿Qué es `grep -a`?
10. Lean esta línea: `Accepted password for root from 192.168.56.102 port 55644 ssh2`.
11. ¿Cómo se restaura un solo archivo? ¿Por qué sin `/` inicial?
12. ¿Por qué el respaldo debe ser posterior a los controles?
13. ¿Por qué la copia debe estar fuera de la VM? ¿Con qué comando?
14. Pasos ante un acceso sospechoso (6) y los tres responsables.
15. ¿Qué persiste tras reiniciar y por qué?
16. ¿Qué riesgos quedan?
17. ¿Qué diferencia hay entre *closed* y *filtered*?
18. ¿Por qué `sudo` en lugar de root directo?
19. ¿Qué evidencia muestra el antes de cada debilidad? (E03, E04, E06, E08, E14)
20. ¿Qué hizo cada uno de ustedes? (el reparto está en el informe, §1.1)

Respuestas: informe §4–§9, notas de las diapositivas y la sección 7 de `GUION_SUSTENTACION.md`.

## 6. Qué falta antes de presentar

El informe incluye capturas reales de P3 y P4; el resto de la validación (P1, P2, P5–P10) figura como «Verificación en vivo» y se demuestra en la sustentación. **Si pueden, saquen esas capturas** con `GUIA_CAPTURAS.md` y regeneren el PDF: la nota de «pruebas comparativas, registros y recuperación» pesa 25 %. Ensayen la demostración completa en las VM al menos dos veces.
