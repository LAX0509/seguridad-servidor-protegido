# Sesión de capturas: lo único que falta del informe

Son **10 capturas** (P1 a P10). Se sacan en una sola sesión de unos 30 minutos, en este orden, porque unas dependen de otras (el respaldo se copia a Kali **antes** de borrar `index.html`, y el reinicio va **al final**). Todo se escribe a mano; no hace falta pasar scripts a las máquinas virtuales.

**Antes de empezar:** en Ubuntu, `ip a` y confirmar que la IP sigue siendo `192.168.56.101` (si cambió, usen la nueva en todos los comandos). Las contraseñas no se muestran al escribirlas: no aparecen en las capturas.

**Cómo guardar cada captura:** en la carpeta `evidencias\pendientes\`, con el ID al inicio del nombre (los nombres de abajo son una sugerencia; solo importa el `P#_` del inicio). Tomen la captura **de la ventana completa de la terminal**, con el comando y su resultado a la vista.

---

## Paso 0 · Servidor: página y respaldo nuevo (sin captura)

Solo si su página aún no es la de la organización (si es la de Apache por defecto, hagan este paso; si ya tienen una propia, **avísame el nombre** y lo cambio en las diapositivas y el informe):

```bash
sudo tee /var/www/html/index.html >/dev/null <<'HTML'
<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Caf&eacute; Monta&ntilde;a S.A.S.</title></head>
<body><h1>Caf&eacute; Monta&ntilde;a S.A.S.</h1><p>Caf&eacute; de origen colombiano, tostado en la monta&ntilde;a.</p>
<p>Sitio de prueba de un laboratorio acad&eacute;mico. Todos los datos son ficticios.</p></body></html>
HTML
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html
```

(La versión completa, con productos y contacto, está en `scripts/06_pagina_organizacion.sh`.)

Respaldo nuevo, **con los controles ya aplicados**, incluyendo las reglas de UFW:

```bash
cd ~
sudo tar -czvf respaldo_servidor.tar.gz /var/www/html /etc/ssh/sshd_config /etc/ufw/ufw.conf /etc/ufw/user.rules /etc/ufw/user6.rules
ls -l respaldo_servidor.tar.gz
```

---

## Servidor (sesión de `juan`)

| ID | Comandos | Debe verse | Archivo |
|---|---|---|---|
| **P3** | `sudo ufw status verbose` | `Status: active`, `Default: deny (incoming), allow (outgoing)`, y `22/tcp` y `80/tcp` en `ALLOW IN` | `P3_ufw_status.png` |
| **P4** | `ls -ld /var/www/html ; ls -l /var/www/html` | `drwxr-xr-x … www-data www-data … /var/www/html` | `P4_permisos_755.png` |
| **P5** | `sudo sshd -T \| grep -Ei '^(permitrootlogin\|passwordauthentication\|maxauthtries)'`<br>`systemctl is-active vsftpd ; systemctl is-enabled vsftpd`<br>`apt list --upgradable 2>/dev/null \| tail -n +2 \| wc -l` | `permitrootlogin no`; `inactive` y `disabled`; el número de paquetes pendientes (idealmente 0) | `P5_sshd_vsftpd_updates.png` |

## Kali

| ID | Comandos | Debe verse | Archivo |
|---|---|---|---|
| **P1** | Navegador en `http://192.168.56.101/` y, en la terminal, `curl -sI http://192.168.56.101/ \| head -n 1` | La página de la organización y `HTTP/1.1 200 OK` (una captura con ambas, o dos) | `P1_sitio_funcionando.png` |
| **P2** | `nmap -sV -p- -T4 --max-retries 1 192.168.56.101` (tarda varios minutos: es normal, el firewall descarta paquetes) | Solo `22/tcp open ssh` y `80/tcp open http`; el 21 no aparece abierto | `P2_nmap_final.png` |
| **P6** | `ssh juan@192.168.56.101` y luego `whoami ; hostname ; id` | `juan`, `ubuntu` y los grupos de `juan` (sin ser root) | `P6_ssh_juan_permitido.png` |
| **P9** | `scp juan@192.168.56.101:~/respaldo_servidor.tar.gz .`<br>`ls -l respaldo_servidor.tar.gz ; sha256sum respaldo_servidor.tar.gz` | La barra de progreso del `scp` y el archivo ya en Kali (si se ve cortada, sacar dos capturas y poner `P9a_` y `P9b_`) | `P9_scp_respaldo_en_kali.png` |

## Borrar y restaurar (servidor + navegador de Kali)

| ID | Qué hacer | Debe verse | Archivo |
|---|---|---|---|
| **P7** | Servidor: `sudo rm /var/www/html/index.html`. Kali: recargar la página en el navegador | La página ya **no** aparece: un «Index of /» vacío o un error | `P7_sitio_sin_index.png` |
| **P8** | Servidor: `cd ~ ; sudo tar -xzvf respaldo_servidor.tar.gz -C / var/www/html/index.html ; ls -l /var/www/html`. Kali: recargar | La página de la organización otra vez funcionando | `P8_sitio_restaurado.png` |

## Al final: reinicio

| ID | Qué hacer | Debe verse | Archivo |
|---|---|---|---|
| **P10** | Servidor: `sudo reboot`; al volver, iniciar sesión y ejecutar en la misma pantalla:<br>`uname -r ; sudo ufw status verbose ; sudo sshd -T \| grep -i permitrootlogin ; systemctl is-active vsftpd ; systemctl is-active apache2` | Kernel `7.0.0-42`, UFW `active`, `permitrootlogin no`, `vsftpd` `inactive`, Apache `active` | `P10_persistencia_reinicio.png` |

Opcional pero recomendable: tras el reinicio, repetir en Kali `curl -sI http://192.168.56.101/ | head -n 1` y `nmap -sV -p21,22,80 192.168.56.101`.

---

## Cuando estén las 10

```powershell
cd "C:\Users\aprendiz.ti\Downloads\proyect grado\seguridad_informatica\informe"
python -I build_informe.py
```

Cada recuadro amarillo «PENDIENTE» se reemplaza por su captura. Si un nombre no empieza por `P#_`, esa captura no se incrusta.

---

## Datos que me tienen que pasar (una sola vez)

Con esto no queda nada amarillo en el PDF ni corchetes en las diapositivas:

1. Nombre completo del segundo integrante, y confirmar que el primero es **Juan Camilo Nieto**.
2. Institución, nombre del docente, y si el docente asignó condiciones distintas para el escenario (o «ninguna»).
3. Quién hizo qué (una o dos líneas por persona) y quiénes figuran como administrador del servidor, responsable de seguridad y contacto de la organización.
4. Incidencia **I03**: cómo le dieron Internet a Ubuntu para `apt upgrade` (por ejemplo, un adaptador NAT extra) y que volvieron a «solo-anfitrión».
5. Incidencia **I08**: por qué falló el `scp` con «No route to host» y cómo lo resolvieron.
6. Confirmar que en **E17** usaron la **misma contraseña de root** que dio acceso en E08.
7. Si la página del sitio ya tenía otro nombre de organización distinto de **Café Montaña S.A.S.**
8. Si la VM de Ubuntu es con escritorio (GNOME) o Server.
