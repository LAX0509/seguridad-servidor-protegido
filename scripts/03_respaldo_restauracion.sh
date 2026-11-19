#!/usr/bin/env bash
# =====================================================================
# 03 - RESPALDO Y RESTAURACION  -  ejecutar en el servidor Ubuntu
# La copia EXTERNA (fuera de la VM del servidor) se hace desde Kali: ver paso R4.
# =====================================================================
set -u
cd ~ || exit 1

echo "[R1] Creando el respaldo (sitio web + configuraciones criticas)..."
# Nota: /etc/ufw/ufw.conf solo guarda ENABLED/LOGLEVEL; las reglas estan en user.rules y user6.rules.
sudo tar -czvf respaldo_servidor.tar.gz \
  /var/www/html /etc/ssh/sshd_config \
  /etc/ufw/ufw.conf /etc/ufw/user.rules /etc/ufw/user6.rules
ls -l respaldo_servidor.tar.gz

echo "[R2] Simulando perdida de datos: se borra el archivo de prueba..."
sudo rm /var/www/html/index.html
echo -n "Titulo de la pagina sin index.html (si Apache lista el directorio, el codigo HTTP sigue siendo 200): "; curl -s http://localhost/ | grep -o -m1 -E "<title>[^<]*</title>"

echo "[R3] Restaurando desde el respaldo (-C / extrae en las rutas originales)..."
sudo tar -xzvf respaldo_servidor.tar.gz -C /
echo -n "Titulo de la pagina tras restaurar: "; curl -s http://localhost/ | grep -o -m1 -E "<title>[^<]*</title>"
ls -l /var/www/html

echo "[R4] Copia externa: ejecutar DESDE KALI ->"
echo "     scp juan@192.168.56.101:~/respaldo_servidor.tar.gz ."
