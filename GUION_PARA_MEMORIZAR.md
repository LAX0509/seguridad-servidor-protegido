# Guion para memorizar (una hoja)

El guion completo está en `GUION_SUSTENTACION.md` y, como notas del orador, en cada diapositiva. Esta hoja es lo que hay que **llevar en la cabeza**: una frase de arranque y tres ideas por bloque. No se memoriza palabra por palabra; se memoriza el orden y las cifras.

## Los 10 bloques

| # | Quién · tiempo | Arranca con… | Tres ideas | Cierra con… |
|---|---|---|---|---|
| 1 | B · 0:45 | «Convertimos un servidor vulnerable en uno protegido **sin dejar de prestar el servicio**.» | Funcional, justificado, con límites · dos VM en red aislada · Ubuntu .101, Kali .102 | «Solo datos ficticios.» |
| 2 | A · 1:45 | «Café Montaña necesita publicar su sitio y administrarlo a distancia.» | Visitantes (80) y administrador `juan` (22) · se protege sitio, configuración y root · 5 debilidades: acceso, permisos, red, servicio, mantenimiento | «Un puerto abierto, por sí solo, no es una vulnerabilidad.» |
| 3 | B · 1:45 | «Este es el antes; el después lo verificamos en vivo.» | E06: 21, 22 y 80 sin filtro · E08: consola root y 227 parches (133 de seguridad) · E14: seis fallos y un acceso aceptado, 00:49 UTC = 19:49 · luego C1–C5 | «Las reglas del 22 y el 80, antes de activar el firewall.» |
| 4 | B · 0:25 | «Después de los cinco controles…» | Navegador · `curl -sI` · 200 OK | «…el sitio sigue funcionando.» |
| 5 | B · 0:55 | «Antes: 21, 22 y 80 abiertos.» | `nmap -p21,22,80` · el 21 sale *filtered* · dos capas: servicio detenido y firewall | «El escaneo completo está en la captura P2.» |
| 6 | B → A · 1:25 | «Escribimos la contraseña **correcta** de root.» | `Permission denied` · `juan` sí entra · `sudo` queda registrado | «Le paso el teclado a A.» |
| 7 | A · 1:20 | «Dueño, grupo y otros.» | 777 = `rwx rwx rwx`, 755 = `rwx r-x r-x` · el dueño es `www-data` (usuario de Apache) · `touch` como `juan` → denegado | «Con 777 habría funcionado.» |
| 8 | A · 1:30 | «`sshd -T` muestra lo que el servidor realmente aplica.» | `permitrootlogin no` = prueba concluyente · `auth.log`: evento, usuario, IP de origen · hora en UTC (−5), `grep -a` | «Los `sudo` también quedan registrados (E13).» |
| 9 | A · 1:30 | «Simulamos una pérdida: borramos `index.html`.» | El sitio ya no aparece · `tar -xzvf … -C / var/www/html/index.html` · rutas sin «/» inicial; como root conserva dueño y permisos | «El sitio vuelve; la copia externa está en Kali.» |
| 10 | B · 0:55 | «Resultado: de tres puertos a dos.» | Root rechazado · 777 → 755 · firewall apagado → deny incoming, FTP detenido, sistema actualizado · **límites:** SSH con contraseña, fuerza bruta, HTTP sin TLS, respaldo manual, escritorio | «Quedamos atentos a sus preguntas.» |

## Las cifras que no pueden fallar

| Dato | Valor |
|---|---|
| Servidor / Kali | 192.168.56.101 / 192.168.56.102 |
| Red | 192.168.56.0/24, solo-anfitrión |
| Versiones | Ubuntu 26.04.1 LTS · OpenSSH 10.2p1 · Apache 2.4.66 · vsftpd 3.0.5 · Nmap 7.98 |
| Antes | puertos 21, 22, 80 · 227 paquetes (133 de seguridad) · permisos 777 |
| Después | puertos 22 y 80 · permisos 755, dueño `www-data` · kernel 7.0.0-42 |
| Registro | `/var/log/auth.log`, UTC; 00:49 UTC = 19:49 en Colombia |
| Hallazgos → controles | H1→C3 · H2→C4 · H3→C5 · H4→C2 · H5→C1 |

## Cómo estudiarlo (3 días)

| Cuándo | Qué hacer |
|---|---|
| **Sáb 7 nov** | Sesión de capturas (ver `GUIA_CAPTURAS.md`). Leer en voz alta las notas de las diapositivas, cada uno las suyas. |
| **Dom 8 nov** | Ensayo con cronómetro y las VM reales, **solo con esta hoja**. Segundo ensayo cambiando quién maneja el teclado. Grabarse el audio y escucharlo. |
| **Lun 9 nov** | Tercer ensayo sin ninguna hoja. Revisar la lista de «Antes de entrar» del guion. Si su turno es el 11, repetir el ensayo ese día por la mañana. |

**Regla de oro:** si no recuerdan algo, digan «eso está en la sección tal del informe» y ábranla. Nunca digan ni muestren una contraseña.

**Para practicar las preguntas:** escríbanme «ensayemos» y les hago las preguntas como si fuera el docente, una por una, y les digo qué les faltó.

---

## AJUSTE IMPORTANTE (control C3 ampliado)

El control C3 ahora es "impedir root por SSH **y restringir el acceso**": además de `PermitRootLogin no` se agregan `AllowUsers juan`, `MaxAuthTries 3` y `LoginGraceTime 30`. Se aplica con `scripts/07_restringir_ssh.sh` (ejecutar en el servidor ANTES de la sustentación y comprobar con `sudo sshd -T | grep -E "permitrootlogin|allowusers|maxauthtries|logingracetime"`).

Frase para decirlo: "Además de bloquear root, restringimos SSH: solo juan puede entrar, con máximo 3 intentos y 30 segundos para autenticarse."
