#!/usr/bin/env bash
# =====================================================================
# 05 - VALIDACION FINAL DESDE KALI (maquina de pruebas)
# Genera las evidencias P1, P2, P6 y P9, y repite la prueba E17.
# Uso:  bash 05_validacion_kali.sh [IP_SERVIDOR] [USUARIO_ADMIN]
# =====================================================================
TARGET="${1:-192.168.56.101}"
ADMIN="${2:-juan}"

echo "### P2 - Nmap tras los controles (mismo escaneo que E06)"
echo "    -T4 y --max-retries 1 solo acortan el tiempo: con UFW descartando paquetes, -p- puede tardar muchos minutos."
nmap -sV -p- -T4 --max-retries 1 "$TARGET"

echo; echo "### P1 - Sitio web disponible"
curl -sI "http://$TARGET/" | head -n 1
echo "(Abra tambien http://$TARGET/ en el navegador de Kali y capture la pagina)"

echo; echo "### E17 - Acceso BLOQUEADO: root por SSH (use la MISMA clave de root que dio acceso en E08)"
ssh -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 "root@$TARGET" 'echo SI_ENTRO_ROOT'

echo; echo "### P6 - Acceso PERMITIDO: usuario administrador"
ssh "$ADMIN@$TARGET" 'echo "Conectado como: $(whoami) en $(hostname)"; id'

echo; echo "### P9 - Respaldo FUERA de la VM del servidor"
scp "$ADMIN@$TARGET:~/respaldo_servidor.tar.gz" .
ls -l respaldo_servidor.tar.gz
sha256sum respaldo_servidor.tar.gz
