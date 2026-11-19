#!/usr/bin/env bash
# =====================================================================
# 01 - ESTADO INICIAL VULNERABLE  (solo para la VM del laboratorio aislado)
# Reproduce las debilidades documentadas en el diagnostico (H1-H5).
# NO ejecutar en equipos reales ni institucionales.
# Ejecutar en el servidor Ubuntu con un usuario que tenga sudo.
# =====================================================================
set -u

echo "[1/5] Instalando servicios: OpenSSH, Apache y FTP..."
sudo apt update
sudo apt install -y openssh-server apache2 vsftpd

# Pagina sencilla de la organizacion ficticia (Cafe Montana S.A.S.)
sudo tee /var/www/html/index.html >/dev/null <<'HTML'
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Caf&eacute; Monta&ntilde;a S.A.S.</title>
<style>
body{font-family:Arial,sans-serif;max-width:720px;margin:40px auto;padding:0 16px;color:#222}
h1{color:#5b3a1e}
footer{margin-top:40px;font-size:.85em;color:#666}
</style>
</head>
<body>
<h1>Caf&eacute; Monta&ntilde;a S.A.S.</h1>
<p>Caf&eacute; de origen colombiano, tostado en la monta&ntilde;a.</p>
<h2>Productos</h2>
<ul><li>Caf&eacute; molido 500 g</li><li>Caf&eacute; en grano 1 kg</li><li>Caf&eacute; de origen &uacute;nico</li></ul>
<h2>Contacto</h2>
<p>contacto@cafemontana.example &middot; Tel. 000 000 0000 (datos ficticios)</p>
<footer>Sitio de prueba de un laboratorio acad&eacute;mico. Todos los datos son ficticios.</footer>
</body>
</html>
HTML

echo "[2/5] H1 - Permitir login SSH directo como root..."
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
echo "      Defina una clave de laboratorio para root (no se escribe en el informe):  sudo passwd root"
sudo systemctl restart ssh

echo "[3/5] H2 - Permisos 777 en el sitio web..."
sudo chmod -R 777 /var/www/html

echo "[4/5] H3 - Firewall desactivado..."
sudo ufw disable

echo "[5/5] H4 - FTP (vsftpd) queda activo por la instalacion, puerto 21/tcp:"
systemctl is-active vsftpd

# H5 (sistema sin actualizar) se da por defecto: NO se ejecuta apt upgrade en este paso.
echo "Listo. Apague la VM y tome la instantanea 'estado inicial vulnerable' en VirtualBox."
