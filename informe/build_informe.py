#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera informe.html y Informe_Final_Seguridad.pdf a partir de plantilla.html,
datos.json, las capturas de ../evidencias y los scripts de ../scripts.

Uso:   python build_informe.py
Las capturas pendientes (P1..P10) se incorporan solas cuando se guardan en
../evidencias/pendientes/ con el prefijo de su ID (p. ej. P1_sitio_web.png).
"""
import html
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

INF = Path(__file__).resolve().parent
RAIZ = INF.parent
EV = RAIZ / "evidencias"
INC = EV / "incidencias"
PEN = EV / "pendientes"
SCR = RAIZ / "scripts"
SALIDA_HTML = INF / "informe.html"
SALIDA_PDF = RAIZ / "Informe_Final_Seguridad.pdf"
EXT = (".png", ".jpg", ".jpeg")

# ---------------------------------------------------------------------------
# Capturas existentes: id -> (archivo, titulo, comando, que_se_observa, que_demuestra)
# ---------------------------------------------------------------------------
EVID = {
    "E01": ("E01_ip_servidor_ubuntu.png", "Dirección IP del servidor Ubuntu",
            "ip a",
            "Interfaz <code>enp0s3</code> con <code>192.168.56.101/24</code> (asignada por DHCP, <i>scope global dynamic</i>) y MAC <code>08:00:27:ce:34:b4</code>.",
            "Identifica el activo evaluado (la IP objetivo de Nmap y SSH) y confirma que está en la red aislada 192.168.56.0/24."),
    "E02": ("E02_instalacion_openssh_server.png", "Instalación de OpenSSH Server",
            "sudo apt install openssh-server",
            "Se despliega <code>openssh-server 1:10.2p1-2ubuntu3.8</code>, se crea el usuario de separación de privilegios <code>sshd</code> y las unidades <code>ssh.service</code> / <code>ssh.socket</code>. Las dos últimas líneas muestran un error de tipeo al abrir nano (ver incidencia I01).",
            "Cumple el requisito de OpenSSH para la administración remota del servidor."),
    "E03": ("E03_apache_permisos777_firewall_apagado.png", "Estado inicial: Apache instalado, permisos 777 y firewall apagado",
            "sudo chmod -R 777 /var/www/html &amp;&amp; sudo ufw disable",
            "Cierre de la instalación de <code>apache2 2.4.66</code> (módulos y sitio <i>000-default</i> habilitados), seguido de <code>sudo chmod -R 777 /var/www/html</code> y <code>sudo ufw disable</code>, que responde «Firewall stopped and disabled on system startup».",
            "Documenta la creación de las debilidades H2 (permisos 777) y H3 (firewall desactivado) sobre un servidor web operativo."),
    "E04": ("E04_instalacion_vsftpd_ftp.png", "Servicio innecesario: instalación de vsftpd",
            "sudo apt install vsftpd -y",
            "Se instala <code>vsftpd 3.0.5-0.4</code> y se crea <code>vsftpd.service</code> habilitado en el arranque (<i>multi-user.target.wants</i>).",
            "Documenta H4: un servicio FTP que el escenario no necesita (el servidor solo debe publicar web y permitir administración remota)."),
    "E05": ("E05_instantanea_estado_inicial_vulnerable.png", "Instantánea del estado inicial vulnerable",
            "VirtualBox → Instantánea → Tomar",
            "La VM <b>UBUNTU_VIRTUAL</b> muestra la instantánea «<b>estado inicial vulnerable</b>» tomada el 4/11/2026 a las 10:28 p. m. A la izquierda aparecen también la máquina de pruebas <i>kali-linux-2026.1-virtualbox-amd64</i>.",
            "Conserva el estado inicial como exige la actividad: permite volver a él y repetir el diagnóstico."),
    "E05b": ("E05b_detalle_instantanea.png", "Detalle ampliado de la instantánea",
             "",
             "Recorte de E05 (derivado, sin alterar): la instantánea «<b>estado inicial vulnerable</b>», «Tomada» el <b>4/11/2026 10:28 p. m.</b>, y debajo «Estado actual (modificado)».",
             "Confirma el nombre y la hora exactos de la instantánea del estado inicial."),
    "E06": ("E06_nmap_inicial_puertos_21_22_80.png", "Diagnóstico con Nmap sobre el estado inicial",
            "nmap -sV -p- 192.168.56.101",
            "Desde Kali, Nmap 7.98 informa 3 puertos abiertos: <code>21/tcp ftp vsftpd 3.0.5</code>, <code>22/tcp ssh OpenSSH 10.2p1 Ubuntu 2ubuntu3.8</code> y <code>80/tcp http Apache httpd 2.4.66</code>. Los otros 65 532 puertos están cerrados («reset»). Duración: 45 s.",
            "Los puertos cerrados responden con <i>reset</i>, es decir, no hay filtrado: el firewall está apagado. Un puerto abierto por sí solo no es una vulnerabilidad: 22 y 80 son necesarios; el 21 no lo es y por eso se hace hallazgo (H4)."),
    "E07": ("E07_ssh_root_intentos_fallidos.png", "Intentos de acceso SSH como root con contraseña incorrecta",
            "ssh root@192.168.56.101",
            "Primera conexión: Kali muestra la huella ED25519 del servidor, se acepta («yes») y se agrega a <i>known_hosts</i>. Dos rondas de tres intentos terminan en «Permission denied (publickey,password)».",
            "El servidor atiende a <code>root</code> por SSH desde la red. Estos rechazos se deben a una contraseña <b>incorrecta</b> (el registro E14 los muestra como <i>Failed password for root</i>) y no a un control de configuración: <b>no</b> son evidencia de protección; ver E17 para la prueba posterior a los controles."),
    "E08": ("E08_ssh_root_acceso_exitoso_inicial.png", "Acceso no autorizado exitoso como root (estado inicial)",
            "ssh root@192.168.56.101",
            "Tras autenticarse con la contraseña de root (no visible), aparece el banner de <b>Ubuntu 26.04.1 LTS</b> (kernel 7.0.0-31-generic), el aviso «<b>227 updates can be applied immediately. 133 of these updates are standard security updates</b>» y el prompt <code>root@ubuntu:~#</code>.",
            "Demuestra H1 explotada: un equipo de la red obtiene una consola con privilegios totales por SSH. También evidencia H5: 227 actualizaciones pendientes, 133 de seguridad."),
    "E09": ("E09_control1_apt_upgrade_en_curso.png", "Control C1: actualización del sistema en curso",
            "sudo apt upgrade -y",
            "La terminal muestra <code>sudo apt upgrade -y</code> desempaquetando paquetes (progreso 24 %). El reloj de la VM marca Nov 6 01:09 (UTC) y VirtualBox indica «estado inicial vulnerable» como base de la VM.",
            "Muestra la aplicación del control de parcheo. El resultado final se comprueba con <code>apt list --upgradable</code> (evidencia {{ref:P5}})."),
    "E10": ("E10_control3_sshd_config_permitrootlogin_no.png", "Control C3: PermitRootLogin no en sshd_config",
            "sudo nano /etc/ssh/sshd_config",
            "El editor nano 8.7.1 muestra <code>/etc/ssh/sshd_config</code> y, en la sección <i>Authentication</i>, la línea <code>PermitRootLogin no</code> sin el <code>#</code> inicial.",
            "Es la directiva que impide el inicio de sesión SSH directo como root; la administración queda a cargo de un usuario sin privilegios que usa <code>sudo</code>."),
    "E11": ("E11_control5_ufw_default_deny.png", "Control C5: política de entrada por defecto «deny»",
            "sudo ufw default deny incoming",
            "UFW responde «Default incoming policy changed to 'deny'».",
            "Establece el principio de mínimo privilegio en red: todo lo entrante se bloquea salvo lo que se permita explícitamente."),
    "E12": ("E12_controles_2_a_5_consolidado.png", "Controles C2 a C5 aplicados en secuencia",
            "systemctl stop/disable vsftpd · nano sshd_config · systemctl restart ssh · chown/chmod · ufw …",
            "Se ven, en orden: <code>stop</code> y <code>disable vsftpd</code> (con «Removed … vsftpd.service»); <code>nano /etc/ssh/sshd_config</code>; <code>systemctl restart ssh</code>; <code>chown -R www-data:www-data</code> y <code>chmod -R 755 /var/www/html</code>; <code>ufw default deny/allow</code>, <code>allow 22/tcp</code>, <code>allow 80/tcp</code> («Rules updated» e «(v6)») y <code>ufw enable</code> → «Firewall is active and enabled on system startup». Arriba, el final de la actualización: <i>update-grub</i> encuentra <code>initrd.img-7.0.0-42-generic</code>, el kernel nuevo.",
            "Las reglas de 22 y 80 se crean <b>antes</b> de activar UFW, de modo que no se pierde la administración remota ni el sitio web. El mensaje «enabled on system startup» indica que el firewall quedó configurado para arrancar con el sistema; se comprueba tras reiniciar en {{ref:P10}}."),
    "E13": ("E13_log_auth_sudo_comandos_root.png", "Registro de auditoría de comandos privilegiados",
            "sudo grep -a \"root\" /var/log/auth.log | tail -n 20",
            "Cada <code>sudo</code> queda registrado con usuario, terminal, directorio y comando: <code>juan : TTY=/dev/pts/0 ; USER=root ; COMMAND=/usr/sbin/ufw default deny incoming</code>, <code>… allow 22/tcp</code>, <code>… allow 80/tcp</code>, <code>… enable</code> (01:28–01:31 UTC), con apertura y cierre de sesión <i>pam_unix</i>. También aparecen las tareas CRON de root.",
            "Da trazabilidad: se puede reconstruir quién aplicó cada control y cuándo. Los registros usan hora UTC (Colombia es UTC−5)."),
    "E14": ("E14_log_auth_sshd_failed_accepted.png", "Registro de autenticación SSH: intentos fallidos y acceso aceptado",
            "sudo grep -a \"sshd\" /var/log/auth.log | tail -n 20",
            "Seis líneas <code>Failed password for root from 192.168.56.102</code> (00:43 y 00:44 UTC, tres por conexión), dos <code>Connection closed by authenticating user root … [preauth]</code>, y luego <code>Accepted password for root from 192.168.56.102 port 55644 ssh2</code> a las 00:49:33, con la sesión cerrada a las 00:55:03. Más abajo: <code>nano /etc/ssh/sshd_config</code> (01:24:42) y <code>Server listening on 0.0.0.0 port 22</code> (01:26:10), el reinicio de SSH tras el cambio.",
            "Permite localizar el evento sospechoso (acceso de root desde 192.168.56.102) y el cambio de configuración posterior. 00:49 UTC equivale a 19:49 hora local, que coincide con la captura E08."),
    "E15": ("E15_respaldo_tar_creado.png", "Creación del respaldo con tar",
            "sudo tar -czvf respaldo_servidor.tar.gz /var/www/html /etc/ssh/sshd_config /etc/ufw/ufw.conf",
            "tar lista <code>/var/www/html/</code>, <code>/var/www/html/index.html</code>, <code>/etc/ssh/sshd_config</code> y <code>/etc/ufw/ufw.conf</code>. El aviso «Removing leading '/'» es normal: guarda rutas relativas.",
            "Respalda el contenido web y las configuraciones críticas, ya con los controles aplicados."),
    "E16": ("E16_restauracion_tar_extraido.png", "Restauración desde el respaldo",
            "sudo tar -xzvf respaldo_servidor.tar.gz -C /",
            "tar extrae <code>var/www/html/</code>, <code>var/www/html/index.html</code>, <code>etc/ssh/sshd_config</code> y <code>etc/ufw/ufw.conf</code> en sus rutas originales (<code>-C /</code>).",
            "El archivo de prueba (<code>index.html</code>) se recupera desde el respaldo. La secuencia completa borrar → sitio caído → restaurar → sitio de vuelta se documenta en {{ref:P7}} y {{ref:P8}}."),
    "E17": ("E17_validacion_ssh_root_denegado.png", "Validación: acceso SSH como root rechazado tras los controles",
            "ssh root@192.168.56.101",
            "Desde Kali, tres solicitudes de contraseña terminan en «Permission denied (publickey,password)».",
            "Con <code>PermitRootLogin no</code> el servidor rechaza el acceso directo de root. El mensaje es idéntico al de los intentos fallidos de E07, por lo que esta captura por sí sola no distingue entre una contraseña incorrecta y el bloqueo por configuración. La comprobación concluyente es la configuración efectiva <code>sshd -T</code> (evidencia {{ref:P5}}), que se muestra en vivo en la sustentación probando además con la contraseña correcta de root."),
}

# Capturas de incidencias: id -> (archivo, titulo, que_se_observa)
INCID = {
    "I01": ("I01_nano_etc_ssh_es_un_directorio.png", "nano no abre la ruta con un espacio",
            "<code>sudo nano /etc/ssh/ sshd_config</code> → nano abre un archivo vacío y avisa «\"/etc/ssh/\" is a directory»."),
    "I02": ("I02_poweroff_bloqueado_por_inhibidor.png", "El apagado normal es bloqueado",
            "<code>sudo poweroff</code> → «Call to PowerOff failed: Operation denied due to active block inhibitor»."),
    "I03": ("I03_apt_upgrade_sin_dns.png", "apt upgrade sin resolución de nombres",
            "Decenas de «Error: Failed to fetch … Temporary failure resolving 'security.ubuntu.com'»."),
    "I04": ("I04_grep_auth_log_binario.png", "grep sobre auth.log devuelve «binary file matches»",
            "<code>sudo grep \"root\" /var/log/auth.log | tail -n 20</code> → «grep: /var/log/auth.log: binary file matches»."),
    "I05": ("I05_tar_error_ruta_ufw_mayuscula.png", "tar con ruta mal escrita (mayúscula y espacio)",
            "<code>… /var/www/html/etc/ssh/sshd_config /etc/Ufw/ufw.conf</code> → «Cannot stat: No such file or directory»."),
    "I06": ("I06_tar_error_falta_espacio_en_ruta.png", "tar con falta de espacio entre dos rutas",
            "<code>… /var/www/html/etc/ssh/sshd_config</code> pegado en una sola ruta → «Cannot stat»."),
    "I07": ("I07_tar_extraer_opcion_c_minuscula.png", "tar -xzvf con la opción -c en minúscula",
            "<code>sudo tar -xzvf respaldo_servidor.tar.gz -c /</code> → «You may not specify more than one '-Acdtrux'…»."),
    "I08": ("I08_scp_no_route_to_host.png", "scp desde Kali sin ruta al servidor",
            "<code>scp juan@192.168.56.101:~/respaldo.tar.gz .</code> → «ssh: connect to host 192.168.56.101 port 22: No route to host»."),
}

# Capturas que aun no existen: id -> (donde, titulo, comando, que_debe_verse)
PEND = {
    "P1": ("Kali", "Sitio web funcionando tras los controles",
           "Navegador en http://192.168.56.101/   (y   curl -I http://192.168.56.101/ )",
           "La página de la organización cargando y «HTTP/1.1 200 OK». Demuestra que los controles no afectaron el servicio."),
    "P2": ("Kali", "Nmap después de los controles",
           "nmap -sV -p- -T4 --max-retries 1 192.168.56.101     (script 05_validacion_kali.sh)",
           "Solo 22/tcp (ssh) y 80/tcp (http) abiertos; el 21 ya no aparece abierto (filtered/closed) y el resto figura como filtered. Compárese con E06."),
    "P3": ("Ubuntu", "Firewall UFW activo y sus reglas",
           "sudo ufw status verbose     (script 04_validacion_ubuntu.sh)",
           "«Status: active», «Default: deny (incoming), allow (outgoing)» y las reglas 22/tcp y 80/tcp en ALLOW IN."),
    "P4": ("Ubuntu", "Permisos corregidos del sitio web",
           "ls -ld /var/www/html ; ls -l /var/www/html",
           "<code>drwxr-xr-x … www-data www-data</code> (755) en lugar de <code>drwxrwxrwx</code> (777)."),
    "P5": ("Ubuntu", "Configuración efectiva de SSH, FTP inactivo y parches pendientes",
           "sudo sshd -T | grep -i permitrootlogin ; systemctl is-active vsftpd ; apt list --upgradable | wc -l",
           "<code>permitrootlogin no</code>, vsftpd <code>inactive</code> y cero (o casi cero) paquetes pendientes."),
    "P6": ("Kali", "Acceso permitido: administrador legítimo por SSH",
           "ssh juan@192.168.56.101 'hostname; id'",
           "Conexión exitosa con el usuario administrador (no root). Es el «acceso permitido» que pide la sustentación, frente al bloqueado de E17."),
    "P7": ("Ubuntu + Kali", "Pérdida simulada: sitio sin index.html",
           "sudo rm /var/www/html/index.html   y recargar http://192.168.56.101/",
           "El navegador mostrando una lista vacía o un error en lugar de la página."),
    "P8": ("Kali", "Sitio recuperado tras la restauración",
           "(después de E16) recargar http://192.168.56.101/",
           "La página de la organización otra vez funcionando: prueba de restauración exitosa."),
    "P9": ("Kali", "Respaldo fuera de la VM del servidor",
           "scp juan@192.168.56.101:~/respaldo_servidor.tar.gz . ; ls -l respaldo_servidor.tar.gz",
           "Barra de progreso del scp y el archivo respaldo_servidor.tar.gz presente en Kali (otra máquina)."),
    "P10": ("Ubuntu + Kali", "Persistencia de los controles después de reiniciar",
            "sudo reboot  → iniciar sesión → bash 04_validacion_ubuntu.sh   (y repetir P1 y P2 desde Kali)",
            "Tras el reinicio: UFW sigue active, vsftpd inactive, permitrootlogin no y el sitio responde."),
}

# ---------------------------------------------------------------------------
esc = html.escape
figuras = {}       # id -> numero de figura
contador = [0]


def hl(texto):
    """[[texto]] -> marcador amarillo visible."""
    return re.sub(r"\[\[(.+?)\]\]", lambda m: '<span class="ph">[' + m.group(1) + "]</span>", texto, flags=re.S)


def buscar_pendiente(pid):
    if not PEN.exists():
        return None
    for p in sorted(PEN.glob(pid + "_*")):
        if p.suffix.lower() in EXT:
            return p
    return None


def existe(eid):
    if eid in EVID:
        return (EV / EVID[eid][0]).exists()
    if eid in INCID:
        return (INC / INCID[eid][0]).exists()
    if eid in PEND:
        return buscar_pendiente(eid) is not None
    raise KeyError(eid)


def figura(eid):
    contador[0] += 1
    n = contador[0]
    figuras[eid] = n
    if eid in EVID:
        archivo, titulo, cmd, observa, demuestra = EVID[eid]
        ruta = "../evidencias/" + archivo
    elif eid in INCID:
        archivo, titulo, observa = INCID[eid]
        cmd, demuestra, ruta = None, None, "../evidencias/incidencias/" + archivo
    else:
        donde, titulo, cmd, debe = PEND[eid]
        p = buscar_pendiente(eid)
        if p is None:
            return (
                '<div class="envivo"><p class="tt">▶ Verificación en vivo · {id} — {t}</p>'
                "<p><b>Dónde:</b> {d}</p><p><b>Comando:</b> <code>{c}</code></p>"
                "<p><b>Resultado esperado:</b> {v}</p>"
                "<p class='nota'>Esta prueba se ejecuta en directo durante la sustentación, como exige la actividad; "
                "su captura se anexa a la carpeta de evidencias.</p></div>"
            ).format(id=eid, t=esc(titulo), d=esc(donde), c=cmd, v=debe)
        observa, demuestra = None, debe
        ruta = "../evidencias/pendientes/" + p.name
    partes = ['<figure><img src="{}" alt="{}">'.format(ruta, esc(titulo)),
              '<figcaption><span class="n">Figura {}.</span> <b>{}</b> · {}</figcaption>'.format(n, eid, esc(titulo)),
              '<div class="expl">']
    if cmd:
        partes.append("<p><b>Comando:</b> <code>{}</code></p>".format(cmd))
    if observa:
        partes.append("<p><b>Qué se observa:</b> {}</p>".format(observa))
    if demuestra:
        partes.append("<p><b>Qué demuestra:</b> {}</p>".format(demuestra))
    partes.append("</div></figure>")
    return "".join(partes)


def ref(eid):
    if existe(eid):
        return eid
    return '<span class="vivo">' + eid + " (en vivo)</span>"


def estado(ids):
    ids = [i.strip() for i in ids.split(",")]
    if all(existe(i) for i in ids):
        return '<span class="ok">✔ Evidenciado</span>'
    if any(existe(i) for i in ids):
        return '<span class="viv">◐ Parcial · resto en vivo</span>'
    return '<span class="viv">▶ En vivo</span>'


def tabla_reparto(d):
    filas = "".join("<tr><td>{}</td><td>{}</td></tr>".format(esc(r["integrante"]), esc(r["tareas"])) for r in d["reparto"])
    return "<table><thead><tr><th style='width:30%'>Integrante</th><th>Actividades realizadas</th></tr></thead><tbody>" + filas + "</tbody></table>"


def tabla_responsables(d):
    filas = "".join("<tr><td><b>{}</b></td><td>{}</td><td>{}</td></tr>".format(esc(r["rol"]), esc(r["nombre"]), esc(r["funcion"])) for r in d["responsables"])
    return "<table><thead><tr><th style='width:22%'>Rol</th><th style='width:22%'>Responsable</th><th>Función</th></tr></thead><tbody>" + filas + "</tbody></table>"


def indice_evidencias():
    filas = []
    for eid, v in EVID.items():
        filas.append((eid, "evidencias/" + v[0], v[1], figuras.get(eid)))
    for eid, v in PEND.items():
        p = buscar_pendiente(eid)
        filas.append((eid, ("evidencias/pendientes/" + p.name) if p else "— (en vivo)", v[1], figuras.get(eid) if p else None))
    for eid, v in INCID.items():
        filas.append((eid, "evidencias/incidencias/" + v[0], v[1], figuras.get(eid)))
    out = ["<table><thead><tr><th>ID</th><th>Archivo</th><th>Contenido</th><th class='c'>Figura</th></tr></thead><tbody>"]
    for eid, arch, tit, fig in filas:
        f = str(fig) if fig else "—"
        pend = ' class="vivo"' if arch.startswith("—") else ""
        out.append("<tr><td><b>{}</b></td><td><code{}>{}</code></td><td>{}</td><td class='c'>{}</td></tr>".format(eid, pend, esc(arch), esc(tit), f))
    out.append("</tbody></table>")
    return "".join(out)


def main():
    datos = json.loads((INF / "datos.json").read_text(encoding="utf-8"))
    tpl = (INF / "plantilla.html").read_text(encoding="utf-8")

    # 1) datos simples
    def dato(m):
        return esc(str(datos[m.group(1)]))
    tpl = re.sub(r"\{\{dato:(\w+)\}\}", dato, tpl)
    tpl = tpl.replace("{{integrantes_lista}}", "<br>".join(esc(i) for i in datos["integrantes"]))
    tpl = tpl.replace("{{reparto_tabla}}", tabla_reparto(datos))
    tpl = tpl.replace("{{responsables_tabla}}", tabla_responsables(datos))
    tpl = tpl.replace("{{svg:diagrama_red}}", (INF / "diagrama_red.svg").read_text(encoding="utf-8"))

    # 2) figuras en orden de aparicion (numeracion automatica)
    tpl = re.sub(r"\{\{fig:(\w+)\}\}", lambda m: figura(m.group(1)), tpl)
    # referencias dentro de los textos del registro
    tpl = re.sub(r"\{\{ref:(\w+)\}\}", lambda m: ref(m.group(1)), tpl)
    tpl = re.sub(r"\{\{estado:([\w, ]+)\}\}", lambda m: estado(m.group(1)), tpl)
    tpl = tpl.replace("{{indice_evidencias}}", indice_evidencias())

    # 3) marcadores [[...]] (antes de insertar scripts, que contienen corchetes propios)
    tpl = hl(tpl)

    # 4) scripts
    def script(m):
        nombre = m.group(1)
        txt = (SCR / nombre).read_text(encoding="utf-8")
        return "<h3><code>{}</code></h3><pre>{}</pre>".format(esc(nombre), esc(txt.rstrip()))
    tpl = re.sub(r"\{\{script:([\w.]+)\}\}", script, tpl)

    SALIDA_HTML.write_text(tpl, encoding="utf-8")
    sin_resolver = re.findall(r"\{\{[^}]+\}\}", tpl)
    if sin_resolver:
        print("ADVERTENCIA: marcadores sin resolver:", sin_resolver)

    # 5) PDF con Edge/Chrome sin interfaz
    navegador = None
    for c in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
        if Path(c).exists():
            navegador = c
            break
    if not navegador:
        print("No se encontró Edge ni Chrome; abra informe.html y use Imprimir → Guardar como PDF.")
        return 1
    perfil = Path(tempfile.gettempdir()) / "edge_perfil_informe"
    if SALIDA_PDF.exists():
        SALIDA_PDF.unlink()
    cmd = [navegador, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--user-data-dir=" + str(perfil), "--print-to-pdf=" + str(SALIDA_PDF),
           SALIDA_HTML.as_uri()]
    subprocess.run(cmd, check=False, timeout=180, capture_output=True)
    # Edge puede devolver el control antes de terminar de escribir el PDF: esperar a que aparezca y se estabilice
    ultimo, estable = -1, 0
    for _ in range(120):
        tam = SALIDA_PDF.stat().st_size if SALIDA_PDF.exists() else 0
        if tam > 0 and tam == ultimo:
            estable += 1
            if estable >= 3:
                break
        else:
            estable = 0
        ultimo = tam
        time.sleep(1)
    pend = [k for k in PEND if not buscar_pendiente(k)]
    print("Figuras incrustadas:", len(figuras))
    print("Capturas pendientes:", ", ".join(pend) if pend else "ninguna")
    print("PDF:", SALIDA_PDF if SALIDA_PDF.exists() else "NO SE GENERÓ")
    return 0 if SALIDA_PDF.exists() else 2


if __name__ == "__main__":
    sys.exit(main())
