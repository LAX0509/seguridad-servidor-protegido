#!/usr/bin/env bash
# =====================================================================
# 02 - CONTROLES DE SEGURIDAD (C1-C5)  -  ejecutar en el servidor Ubuntu
# Cada bloque responde a un hallazgo del diagnostico.
# =====================================================================
set -u

echo "[C1] (H5) Actualizando el sistema. Requiere salida a Internet temporal."
sudo apt update && sudo apt upgrade -y

echo "[C2] (H4) Deshabilitando el servicio innecesario vsftpd..."
sudo systemctl stop vsftpd && sudo systemctl disable vsftpd

echo "[C3] (H1) Bloqueando el login SSH directo como root..."
sudo cp -a /etc/ssh/sshd_config /etc/ssh/sshd_config.bak      # copia previa por si hay que revertir
sudo sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sshd -t && sudo systemctl restart ssh                    # sshd -t valida la sintaxis antes de reiniciar

echo "[C4] (H2) Corrigiendo permisos del sitio web..."
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "[C5] (H3) Configurando el firewall UFW..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp        # administracion SSH  (ANTES de activar UFW, para no perder el acceso)
sudo ufw allow 80/tcp        # sitio web HTTP
sudo ufw --force enable
sudo ufw status verbose
