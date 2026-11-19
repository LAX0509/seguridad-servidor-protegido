#!/usr/bin/env bash
# =====================================================================
# 07 - RESTRINGIR SSH (parte del control C3)  -  ejecutar en el servidor
# Deja: PermitRootLogin no, AllowUsers juan, MaxAuthTries 3, LoginGraceTime 30
# ANTES: tener una sesion SSH de juan abierta y probar desde otra terminal.
# =====================================================================
set -eu
CFG=/etc/ssh/sshd_config
USUARIO=juan

sudo cp -a "$CFG" "$CFG.bak.$(date +%Y%m%d%H%M%S)"     # copia previa para revertir

poner() {   # poner CLAVE VALOR  -> reemplaza la linea (comentada o no) o la agrega al final
  if sudo grep -Eq "^[#[:space:]]*$1[[:space:]]" "$CFG"; then
    sudo sed -i -E "s|^[#[:space:]]*$1[[:space:]].*|$1 $2|" "$CFG"
  else
    echo "$1 $2" | sudo tee -a "$CFG" >/dev/null
  fi
}

poner PermitRootLogin no
poner AllowUsers "$USUARIO"
poner MaxAuthTries 3
poner LoginGraceTime 30

echo "[1] Validando la sintaxis (sin salida = correcto)"
sudo sshd -t

echo "[2] Reiniciando ssh"
sudo systemctl restart ssh

echo "[3] Configuracion efectiva:"
sudo sshd -T | grep -E "^(permitrootlogin|allowusers|maxauthtries|logingracetime)"

echo "Ahora, desde OTRA terminal: ssh $USUARIO@192.168.56.101 (debe entrar) y ssh root@192.168.56.101 (debe dar Permission denied)."
