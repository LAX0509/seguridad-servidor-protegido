#!/usr/bin/env bash
# =====================================================================
# 06 - PAGINA DE LA ORGANIZACION FICTICIA (Cafe Montana S.A.S.)
# Crea (o restablece) /var/www/html/index.html con dueno www-data y
# permisos 755, es decir, en el estado PROTEGIDO.
# Ejecutar en el servidor Ubuntu ANTES de generar el respaldo (script 03).
# =====================================================================
set -u

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
sudo chown -R www-data:www-data /var/www/html
sudo chmod -R 755 /var/www/html

echo "Pagina creada. Permisos actuales:"
ls -ld /var/www/html
ls -l  /var/www/html
echo -n "Titulo servido por Apache: "
curl -s http://localhost/ | grep -o -m1 -E "<title>[^<]*</title>"