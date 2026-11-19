#!/usr/bin/env bash
# =====================================================================
# 04 - VALIDACION FINAL EN EL SERVIDOR UBUNTU
# Genera las evidencias P3, P4 y P5. Para P10 (persistencia): ejecutar
#   sudo reboot
# y, tras volver a iniciar sesion, correr este mismo script otra vez.
# Guarda ademas una copia en texto en ~/validacion_ubuntu.txt
# =====================================================================
OUT=~/validacion_ubuntu.txt
{
echo "=== $(date '+%F %T %Z') | $(hostname) | $(lsb_release -ds) | kernel $(uname -r) ==="

echo; echo "### P3 - Firewall (UFW)"
sudo ufw status verbose

echo; echo "### P4 - Permisos del sitio web (esperado: 755, dueno www-data)"
ls -ld /var/www/html
ls -l  /var/www/html

echo; echo "### P5 - Configuracion efectiva de SSH, estado de FTP y actualizaciones"
sudo sshd -T | grep -Ei '^(permitrootlogin|passwordauthentication|maxauthtries)'
echo -n "vsftpd activo: ";                  systemctl is-active vsftpd
echo -n "vsftpd habilitado en el arranque: "; systemctl is-enabled vsftpd
echo -n "Paquetes con actualizacion pendiente: "; apt list --upgradable 2>/dev/null | tail -n +2 | wc -l

echo; echo "### Puertos en escucha"
sudo ss -tlnp

echo; echo "### Apache"
systemctl is-active apache2
curl -sI http://localhost | head -n 1
} 2>&1 | tee "$OUT"
