# Asistente Terminal para Termux

Asistente de línea de comandos para Android (Termux). Busca archivos, renombra, ejecuta comandos y responde preguntas. Sin dependencias externas, solo Python 3.

**Plataforma:** Android (Termux) · Linux · macOS · Windows

## Instalación en Termux

```bash
# Instalar Termux desde F-Droid (no desde Play Store)

# Dentro de Termux:
pkg install python git
git clone https://github.com/feralegria94/asistente_terminal.git
cd asistente_terminal
python3 asistente.py
```

## Uso

### Modo chat interactivo

```bash
python3 asistente.py
```

Escribe comandos en lenguaje natural:

```
❯ buscar foto
Encontré 3 resultado(s) para 'foto':
📄 foto_perfil.jpg (245.3KB)
📁 fotos/
📄 captura_pantalla.png (1.2MB)

❯ listar
📁 Descargas/
📁 Documents/
📄 notas.txt (2.1KB)
📄 lista_compras.md (512B)

❯ renombrar notas viejo_notas.txt
Renombrado: notas → viejo_notas.txt

❯ ejecuta df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/root        58G   23G   33G  41% /

❯ hora
14:32:07 15/10/2026

❯ dónde estoy
Estás en: /data/data/com.termux/files/home
```

### Comandos CLI directos (sin modo chat)

```bash
python3 asistente.py buscar archivo.txt
python3 asistente.py listar /sdcard
python3 asistente.py renombrar viejo.txt nuevo.txt
python3 asistente.py version
python3 asistente.py ayuda
```

## Comandos disponibles en chat

| Comando | Qué hace |
|---------|----------|
| `buscar <patrón>` | Busca archivos en el directorio actual |
| `listar [ruta]` | Lista archivos con tamaño |
| `renombrar <viejo> <nuevo>` | Renombra un archivo |
| `ejecuta <comando>` | Ejecuta un comando del sistema |
| `sistema` | Información del sistema |
| `dónde estoy` | Directorio de trabajo actual |
| `hora` | Hora y fecha actual |
| `ayuda` | Muestra la lista de comandos |
| `salir` | Cierra el asistente |

## Sin dependencias

Funciona solo con Python 3 estándar. No necesita `pip install` ni conexión a internet. El historial se guarda en `~/.asistente_terminal/`.

## Ideas futuras

- [ ] Integración con Ollama local para respuestas con IA
- [ ] Reconocimiento de voz
- [ ] Resumen de archivos de texto
- [ ] Gestión de tareas y recordatorios

---

Creado por [Fernando Alegría](https://github.com/feralegria94) · [MR.COM Soluciones](https://mrcomsoluciones.cl)
