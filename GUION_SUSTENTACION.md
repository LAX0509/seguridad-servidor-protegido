# Guion de sustentación — 15 minutos

**Proyecto:** De servidor vulnerable a servidor protegido · **Fechas:** 9 y 11 de noviembre de 2026
**Quién es quién:** `A` = quien maneja el **servidor Ubuntu** · `B` = quien maneja **Kali** (pruebas). Si en su reparto real es al revés, cambien las letras; lo importante es que **ambos hablen** y que cada uno pueda explicar **cualquier** comando.

**Diapositivas** (cada una trae como notas del orador el texto de este guion): https://claude.ai/artifact/C3Tqc29qKCRQzFyjtMMb48

> Del enunciado: los 15 minutos **incluyen** el escenario y los riesgos, la demostración y las preguntas. El estado inicial puede mostrarse con evidencias; **el estado protegido hay que verificarlo en vivo**.

---

## 1. Qué exige el enunciado y dónde lo cumple este guion

| Debe mostrar | Bloque del guion | Minuto |
|---|---|---|
| Presentar escenario y riesgos | 1 y 2 | 0:00 – 2:30 |
| Comparar una debilidad inicial con su corrección | 3 (antes, en capturas, 2:30 – 4:15) + 5 y 6 (después, en vivo, 4:40 – 7:00) | 2:30 – 7:00 |
| Sitio funcionando | 4 | 4:15 |
| Un acceso permitido y uno bloqueado | 6 | 5:35 |
| Explicar permisos | 7 | 7:00 |
| Localizar un registro | 8 | 8:20 |
| Restaurar un archivo | 9 | 9:50 |
| Preguntas individuales | 11 | 12:15 – 15:00 |

Criterios de evaluación a tener presentes: diagnóstico y justificación de riesgos 20 % · controles y funcionalidad 30 % · pruebas comparativas, registros y recuperación 25 % · documentación y reproducibilidad 10 % · sustentación y dominio individual 15 %.

## 2. Plano de tiempos

| # | Min | Quién | Qué | Diapositivas |
|---|---|---|---|---|
| 1 | 0:00 – 0:45 | B | Apertura, objetivo y laboratorio | 1 a 3 |
| 2 | 0:45 – 2:30 | A | Escenario y riesgos (H1–H5) | 4 y 5 |
| 3 | 2:30 – 4:15 | B | Estado inicial (evidencias) y controles aplicados | 6 a 10 |
| 4 | 4:15 – 4:40 | B | Sitio funcionando | 11 y navegador de Kali |
| 5 | 4:40 – 5:35 | B | Nmap: antes vs. ahora | Terminal de Kali |
| 6 | 5:35 – 7:00 | B → A | Root bloqueado y `juan` permitido | Terminal de Kali |
| 7 | 7:00 – 8:20 | A | Permisos 777 → 755 | 12 y terminal (sesión de `juan`) |
| 8 | 8:20 – 9:50 | A | Configuración efectiva y registros | 13 y terminal |
| 9 | 9:50 – 11:20 | A (B en el navegador) | Borrar y restaurar un archivo | 14, terminal y navegador |
| 10 | 11:20 – 12:15 | B | Resultado y limitaciones | 15 y 16 |
| 11 | 12:15 – 15:00 | ambos | Preguntas | 17 (la 18 es de respaldo) |

**Si van atrasados:** salten el Nmap en vivo (bloque 5) y muestren la captura P2. **Si van adelantados:** muestren la persistencia tras reinicio (captura P10) o la configuración E10. Nunca recorten los seis requisitos de la sección 1.

---

## 3. Antes de entrar (10 minutos antes)

- [ ] Las dos VM encendidas, en red **solo-anfitrión**. En Ubuntu: `ip a` y confirmar que la IP sigue siendo `192.168.56.101` (es DHCP; si cambió, es la causa más probable del «No route to host» de la incidencia I08). Reemplacen la IP en todos los comandos.
- [ ] En Ubuntu: `bash ~/04_validacion_ubuntu.sh` → UFW `active`, `permitrootlogin no`, `vsftpd` inactivo, Apache activo.
- [ ] `ls -l ~/respaldo_servidor.tar.gz` existe y `tar -tzf ~/respaldo_servidor.tar.gz | grep index.html` muestra `var/www/html/index.html`.
- [ ] **El respaldo debe ser de después de los controles.** No restauren nunca un respaldo del estado vulnerable: traería `PermitRootLogin yes`.
- [ ] En Kali: el archivo `respaldo_servidor.tar.gz` ya copiado con `scp` (evidencia de copia fuera de la VM).
- [ ] Sitio abierto en el navegador de Kali en `http://192.168.56.101/`.
- [ ] Informe PDF abierto en el computador del anfitrión con marcadores en §2.1, §4.2 y §8, y las capturas E06, E08 y E14 a mano.
- [ ] Letra grande en las terminales (Ctrl y `+`). Una sesión SSH de `juan` ya abierta en una terminal aparte como respaldo.
- [ ] **Contraseñas:** se escriben sin mostrarlas y **no se dicen en voz alta**. No abran el archivo de comandos de Descargas: contiene la clave de laboratorio de root.
- [ ] Cronómetro visible para ambos.

---

## 4. Guion minuto a minuto

### Bloque 1 · 0:00 – 0:45 · B · Apertura
**Pantalla:** diapositivas 1 a 3 (portada, objetivo y laboratorio).

> «Buenos días. Somos [nombre A] y [nombre B]. Nuestro proyecto convierte un servidor web vulnerable en uno protegido **sin dejar de prestar el servicio**. No buscamos un servidor invulnerable, sino uno funcional, justificado y con sus limitaciones reconocidas.
> El laboratorio tiene dos máquinas virtuales en una red aislada: un servidor **Ubuntu** con Apache, OpenSSH y UFW, en la 192.168.56.101, y una máquina **Kali** con Nmap y cliente SSH, en la 192.168.56.102. Solo usamos datos ficticios.»

### Bloque 2 · 0:45 – 2:30 · A · Escenario y riesgos
**Pantalla:** diapositivas 4 y 5 (escenario y debilidades).

> «La organización ficticia [nombre] necesita publicar su sitio web y administrarlo a distancia. Hay dos tipos de usuarios: los **visitantes**, que solo leen la página por el puerto 80, y el **administrador**, que entra por SSH, puerto 22, con el usuario `juan`. Lo que hay que proteger es el **sitio** —que no lo modifiquen ni se caiga—, la **configuración** del servidor y la **cuenta root**. No se necesita FTP.
> Dejamos **cinco debilidades de cinco categorías distintas**:»

| ID | Categoría | Debilidad | Por qué importa |
|---|---|---|---|
| H1 | Acceso | `PermitRootLogin yes` | Quien adivine una contraseña obtiene control total |
| H2 | Permisos | `chmod -R 777 /var/www/html` | Cualquiera puede modificar o borrar el sitio |
| H3 | Red | `ufw disable` | Todo lo que escuche queda expuesto |
| H4 | Servicio innecesario | `vsftpd` en el puerto 21 | Superficie extra; FTP viaja sin cifrar |
| H5 | Mantenimiento | 227 paquetes pendientes, 133 de seguridad | Fallos ya corregidos siguen abiertos |

> «Un puerto abierto, por sí solo, no es una vulnerabilidad: el 22 y el 80 están abiertos porque el escenario los necesita. Priorizamos como **alta** H1, H2, H3 y H5, porque dan control, permiten modificar el sitio o dejan todo el equipo sin defensa, y como **media** H4, que amplía la superficie sin dar acceso directo.»

### Bloque 3 · 2:30 – 4:15 · B · Estado inicial (evidencias) y controles
**Pantalla:** diapositivas 6, 7 y 8 (capturas E06, E08, E14) y luego 9 y 10 (controles).

> «Este es el **antes**; lo mostramos con evidencias, y el **después** lo verificamos ahora en vivo.
> **E06, Nmap:** puertos 21, 22 y 80 abiertos, y el resto *cerrado* con respuesta de reinicio: no había ningún filtrado.
> **E08:** desde Kali entramos por SSH como root y obtuvimos una consola `root@ubuntu`. El mismo aviso muestra **227 actualizaciones pendientes, 133 de seguridad**.
> **E14, el registro:** seis `Failed password for root` y luego un `Accepted password for root` desde 192.168.56.102, a las 00:49 UTC, es decir, 19:49 hora de Colombia.
> Antes de aplicar los controles dejamos una instantánea de VirtualBox, «estado inicial vulnerable».»
>
> **Controles (diapositivas 9 y 10, unos 45 s):** «Cada hallazgo tiene su control: C1, actualizar el sistema (H5); C2, detener y deshabilitar FTP (H4); C3, `PermitRootLogin no` (H1); C4, dueño `www-data` y permisos 755 (H2); y C5, firewall con `deny incoming` y `allow` solo para el 22 y el 80 (H3). Las reglas del 22 y el 80 se crean *antes* de activar el firewall, para no perder la sesión SSH.»

### Bloque 4 · 4:15 – 4:40 · B · Sitio funcionando (en vivo)
**Kali:** navegador en `http://192.168.56.101/` y, en la terminal:
```bash
curl -sI http://192.168.56.101/ | head -n 1
```
**Esperado:** la página de la organización y `HTTP/1.1 200 OK`.

> «Después de los cinco controles, el sitio sigue funcionando.»

### Bloque 5 · 4:40 – 5:35 · B · Nmap, antes vs. ahora (en vivo)
```bash
nmap -sV -p21,22,80 192.168.56.101
```
**Esperado:** `21/tcp filtered`, `22/tcp open ssh (OpenSSH 10.2p1)`, `80/tcp open http (Apache 2.4.66)`.

> «Antes: 21, 22 y 80 abiertos y sin filtro. Ahora el 21 aparece **filtrado**: el servicio está detenido *y además* el firewall lo bloquea; son dos capas. Solo quedan abiertos los dos servicios que el escenario necesita. El escaneo completo de los 65 535 puertos está en la captura P2; en vivo escaneamos solo estos tres porque UFW descarta los paquetes y el escaneo completo tarda varios minutos.»

### Bloque 6 · 5:35 – 7:00 · B → A · Acceso bloqueado y acceso permitido (en vivo)
**Bloqueado (B):** usar la **misma contraseña de root que dio acceso en E08** (si no, la prueba no demuestra nada):
```bash
ssh -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 root@192.168.56.101
```
**Esperado:** `Permission denied, please try again.` / `Permission denied (publickey,password).`

> «Escribimos la contraseña **correcta** de root, la misma de la evidencia E08, y el servidor la rechaza. Si entrara, sería porque el control falló.»

**Permitido (B):**
```bash
ssh juan@192.168.56.101
whoami; hostname; id
```
**Esperado:** `juan`, `ubuntu`, grupos de `juan` (sin ser root).

> «El administrador legítimo sí entra, con un usuario sin privilegios; para tareas de administración usa `sudo`, y eso queda registrado. **Le paso el teclado a [A], que ya está dentro del servidor.**»

### Bloque 7 · 7:00 – 8:20 · A · Permisos (en vivo)
```bash
ls -ld /var/www/html
ls -l /var/www/html
touch /var/www/html/prueba.txt
```
**Esperado:** `drwxr-xr-x … www-data www-data …` y `touch` → `Permission denied`.

> «Cada archivo tiene tres juegos de permisos: dueño, grupo y otros. **Antes** estaba en **777**: lectura, escritura y ejecución para todos, o sea, cualquiera podía borrar o reemplazar el sitio. **Ahora** está en **755**, `rwx r-x r-x`: solo el dueño, `www-data`, que es el usuario con el que corre Apache, puede escribir; los demás leen y recorren. Lo comprobamos: `juan`, que es "otros" para este directorio, intenta crear un archivo y el sistema se lo niega. Con 777 habría funcionado.»

### Bloque 8 · 8:20 – 9:50 · A · Configuración efectiva y registros (en vivo)
```bash
sudo sshd -T | grep -i permitrootlogin
sudo grep -a "sshd" /var/log/auth.log | tail -n 8
```
**Esperado:** `permitrootlogin no`; en el registro, los intentos de root de hace un minuto desde 192.168.56.102 (normalmente `Failed password for root`; el texto exacto puede variar) y el `Accepted password for juan from 192.168.56.102`.

> «`sshd -T` muestra la configuración **que el servidor realmente está aplicando**: `permitrootlogin no`. Esta es la prueba concluyente del control, porque en el registro un intento de root rechazado puede verse igual que una contraseña equivocada.
> Los accesos y la autenticación se guardan en `/var/log/auth.log`. Cada línea trae fecha, equipo, proceso `sshd`, el evento, el usuario y la **IP de origen**. Aquí están los intentos de root que acabamos de hacer desde la .102 y el acceso aceptado de `juan`. La hora está en UTC: a la de Colombia hay que restarle cinco horas. Con `grep -a` porque el archivo contiene caracteres no imprimibles. Las órdenes con `sudo` también quedan registradas: la captura E13 muestra quién aplicó cada regla del firewall y cuándo.»

### Bloque 9 · 9:50 – 11:20 · A (y B en el navegador) · Borrar y restaurar un archivo (en vivo)
```bash
cd ~
ls -l respaldo_servidor.tar.gz
sudo rm /var/www/html/index.html
```
**B:** recarga el navegador → ya no aparece la página (verá «Index of /» vacío o un error; **juzguen por lo que se ve, no por el código HTTP**: Apache puede seguir contestando 200 con la lista del directorio).
```bash
sudo tar -xzvf respaldo_servidor.tar.gz -C / var/www/html/index.html
ls -l /var/www/html
```
**B:** recarga → la página vuelve. **Esperado:** `index.html` otra vez con dueño `www-data`.

> «El respaldo es un `.tar.gz` con el sitio y las configuraciones críticas, y tiene copia **fuera de la máquina virtual**: la bajamos a Kali con `scp` [B muestra `ls -l respaldo_servidor.tar.gz` en Kali]. Simulamos una pérdida borrando `index.html`: el sitio deja de mostrarse. Restauramos **solo ese archivo**. `tar` guarda las rutas sin la barra inicial, y `-C /` las extrae desde la raíz, o sea, en su ubicación original. Como lo hace root, conserva el dueño y los permisos. El sitio vuelve.»

### Bloque 10 · 11:20 – 12:15 · B · Resultado y limitaciones
**Pantalla:** diapositivas 15 y 16 (resultado y limitaciones).

> «Resultado: de tres puertos abiertos sin filtro a dos, los que el escenario necesita; root ya no entra por SSH; el sitio pasó de 777 a 755 con dueño `www-data`; el firewall pasó de apagado a denegar todo lo entrante salvo 22 y 80; FTP está detenido y deshabilitado; y el sistema está actualizado. Cada cambio responde a un hallazgo y tiene su prueba, y el sitio y la administración legítima siguen funcionando.
> **Limitaciones que reconocemos:** SSH sigue aceptando contraseñas, así que falta limitar los usuarios (`AllowUsers`), usar llaves y restringir el origen; no hay protección contra fuerza bruta; el sitio va por HTTP sin cifrar; el respaldo es manual; y nuestra máquina es Ubuntu con escritorio [confirmar], no Server. Están descritas como riesgos pendientes en el informe. Quedamos atentos a sus preguntas.»

---

## 5. Si algo falla en vivo (plan B)

| Problema | Qué hacer |
|---|---|
| Kali no llega al servidor / «No route to host» | `ip a` en Ubuntu: la IP DHCP pudo cambiar. Corrijan el comando. Si no se resuelve en 30 s, pasen a las capturas (P1–P9 y E-series) y sigan. |
| Nmap tarda | Cancelen con Ctrl+C y muestren P2. No esperen. |
| `ssh juan@…` se queda colgado | Usen la sesión de `juan` que dejaron abierta aparte; o la consola de VirtualBox del servidor. |
| `touch` **sí** crea el archivo | No sigan adelante sin entenderlo: `ls -ld /var/www/html`; si dice 777, los controles no persisten. Bórrenlo con `sudo rm` y expliquen la causa. |
| La restauración dice «Not found in archive» | `tar -tzf respaldo_servidor.tar.gz \| grep index` para ver el nombre exacto (sin barra inicial). |
| Se borró `index.html` y la restauración de un solo archivo falla | Restauren con la extracción completa `sudo tar -xzvf respaldo_servidor.tar.gz -C /` (es lo que muestra la captura E16), **solo** si el respaldo es posterior a los controles. |
| Se les olvida un dato | Digan «eso está en la sección X del informe» y ábranla; es válido. |

---

## 6. Chuleta de comandos (para pegar/ensayar)

**Kali**
```bash
curl -sI http://192.168.56.101/ | head -n 1
nmap -sV -p21,22,80 192.168.56.101
ssh -o PubkeyAuthentication=no -o NumberOfPasswordPrompts=1 root@192.168.56.101
ssh juan@192.168.56.101
ls -l respaldo_servidor.tar.gz
```
**Ubuntu (sesión de `juan`)**
```bash
ls -ld /var/www/html ; ls -l /var/www/html
touch /var/www/html/prueba.txt
sudo sshd -T | grep -i permitrootlogin
sudo grep -a "sshd" /var/log/auth.log | tail -n 8
cd ~ ; ls -l respaldo_servidor.tar.gz
sudo rm /var/www/html/index.html
sudo tar -xzvf respaldo_servidor.tar.gz -C / var/www/html/index.html
ls -l /var/www/html
```

| Comando | Qué hace (para el dominio individual) |
|---|---|
| `nmap -sV -p-` | Escanea todos los puertos y detecta la versión del servicio |
| `ssh root@IP` | Intenta entrar al servidor como el superusuario |
| `sudo sshd -T` | Muestra la configuración efectiva de SSH (la que está aplicando) |
| `PermitRootLogin no` | `sshd` rechaza el login directo de root, aunque la clave sea correcta |
| `chmod -R 755` / `chown -R www-data:www-data` | Cambia permisos / dueño de forma recursiva |
| `systemctl stop` / `disable` | Detiene el servicio ahora / evita que arranque con el sistema |
| `ufw default deny incoming` | Bloquea por defecto todo lo entrante |
| `ufw allow 22/tcp`, `80/tcp` | Excepciones: SSH y HTTP |
| `ufw enable` | Activa el firewall y lo deja persistente tras reiniciar |
| `grep -a "sshd" /var/log/auth.log` | Filtra los eventos de SSH (`-a`: trata el archivo como texto) |
| `tar -czvf` / `-xzvf -C /` | Crea / extrae el respaldo comprimido (en su ruta original) |
| `scp juan@IP:~/archivo .` | Copia el archivo a la máquina actual (fuera de la VM) |

---

## 7. Preguntas probables y respuestas modelo

**Diagnóstico y riesgos**
1. **¿Por qué un puerto abierto no es una vulnerabilidad?** Porque depende de si el servicio es necesario y cómo está configurado. 22 y 80 están abiertos a propósito; lo que reportamos es lo que añade riesgo: root por SSH, permisos 777, firewall apagado, FTP innecesario, sistema sin parches.
2. **¿Por qué H4 es «media» y las demás «altas»?** Las altas permiten tomar el control, modificar el sitio o dejan todo el equipo sin defensa. FTP amplía la superficie, pero por sí solo no da acceso directo.
3. **¿Por qué en Nmap inicial el resto de puertos decía «closed» y ahora «filtered»?** Sin firewall, el sistema contesta con un reinicio (*closed*). Con UFW en `deny`, descarta los paquetes y Nmap no recibe respuesta (*filtered*).

**Controles**
4. **¿Por qué prohibir root por SSH?** Es la cuenta más conocida y atacada. Con un usuario normal más `sudo` hay trazabilidad: queda registrado quién hizo qué.
5. **¿Cómo prueban que fue el control y no una contraseña equivocada?** Tres evidencias: la misma contraseña que funcionó en E08 ahora es rechazada (E17), `sshd -T` muestra `permitrootlogin no`, y la edición de `sshd_config` está en E10.
6. **¿Por qué `allow 22` *antes* de `enable`?** Para no perder la sesión SSH: activar UFW con `deny incoming` y sin la excepción habría cortado la administración.
7. **¿Qué diferencia hay entre `deny incoming` y `allow outgoing`?** Lo primero bloquea las conexiones que llegan; lo segundo deja que el servidor salga a Internet (actualizaciones, respuestas al visitante).
8. **¿Por qué `stop` y `disable` y no desinstalar vsftpd?** `stop` cierra el puerto ahora y `disable` evita que vuelva al reiniciar. Dejamos el paquete para poder revertir en el laboratorio; en producción se desinstalaría. Y aunque se reactivara, UFW lo bloquea.
9. **¿Por qué 755 en los archivos y no 644?** Aplicamos 755 recursivo por simplicidad. Lo más fino es 755 para directorios y 644 para archivos (`find /var/www/html -type f -exec chmod 644 {} +`). Está como mejora.
10. **¿Por qué `www-data` es el dueño?** Es el usuario con el que corre Apache; así el servidor web es el dueño legítimo y el resto solo lee.
11. **¿Y si `apt upgrade` rompe algo?** Por eso existe la instantánea previa de VirtualBox, y el respaldo; además el sitio es estático y se verificó después.

**Registros y recuperación**
12. **¿Dónde están los registros y qué hora usan?** `/var/log/auth.log`, en UTC; Colombia es UTC−5. En E14, 00:49 UTC = 19:49 locales.
13. **¿Qué hacen ante un acceso sospechoso?** (1) Confirmar en los registros: IP, usuario, hora. (2) Contener: bloquear la IP en UFW, cerrar sesiones, cambiar claves. (3) Preservar evidencia: copiar el log y tomar instantánea. (4) Erradicar y recuperar: verificar permisos y configuración, restaurar desde el respaldo externo. (5) Notificar al contacto de la organización. (6) Mejorar los controles. Responsables: administrador del servidor, responsable de seguridad y contacto de la organización.
14. **¿Qué incluye el respaldo y dónde está?** El sitio (`/var/www/html`) y las configuraciones críticas (`sshd_config` y las de UFW). Está en el servidor y una copia en Kali, fuera de la VM, copiada con `scp`. Una copia en la misma máquina no sirve si esa máquina se pierde. Nota: `ufw.conf` solo guarda `ENABLED`; las reglas están en `user.rules` y `user6.rules`, que el script 03 sí incluye.
15. **¿Cómo restauran un solo archivo?** Con `tar -xzvf respaldo.tar.gz -C / ruta/sin/barra/inicial`; el nombre se consulta con `tar -tzf`.
16. **¿Los controles persisten tras reiniciar?** Sí: UFW queda habilitado, `disable` evita que arranque vsftpd, y `sshd_config`, el dueño y los permisos están en disco. Evidencia: captura P10.

**Limitaciones**
17. **¿Qué riesgos quedan?** SSH con contraseña (sin llaves, sin `AllowUsers`, sin límite de origen ni fail2ban), HTTP sin TLS, respaldo manual sin programar ni cifrar, y sin monitoreo central de registros.
18. **¿Por qué Ubuntu con escritorio y no Server?** [Confirmen con su caso real.] Los paquetes y controles son los mismos; lo declaramos como limitación y en un entorno real usaríamos Server para reducir la superficie.

**Preguntas individuales:** quien no manejó una parte debe poder explicarla igual. Repártanse en el ensayo «¿qué hace este comando y por qué?» sobre la tabla de la sección 6.

---

## 8. Plan de ensayo

| Cuándo | Qué |
|---|---|
| **Hoy, 6 de noviembre** | Completar las capturas pendientes P1–P10 con los scripts `04` y `05`, llenar `informe/datos.json`, regenerar el PDF. |
| **7–8 de noviembre** | Ensayo completo con cronómetro y en las VM reales: 3 veces. Una de ellas, **intercambiando** quién maneja el teclado. |
| **Víspera de su turno** | Revisar la lista de la sección 3; verificar la IP y que el respaldo sea posterior a los controles. |
| **Día de la sustentación** | Encender las VM 15 minutos antes; llevar el PDF y las capturas en el computador. |

Tras cada ensayo, anoten dónde se pasaron de tiempo y recorten de ahí; el bloque 8 suele ser el más largo.

---

## AJUSTE: C3 ampliado (restringir SSH)

Al explicar C3 (bloque de root/juan) agregar: "Además de PermitRootLogin no, restringimos SSH con AllowUsers juan, MaxAuthTries 3 y LoginGraceTime 30." Aplicarlo antes con `scripts/07_restringir_ssh.sh` y mostrar `sudo sshd -T | grep -E "permitrootlogin|allowusers|maxauthtries|logingracetime"` en el paso del registro.
