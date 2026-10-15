#!/usr/bin/env python3
"""
asistente_terminal — Asistente de línea de comandos para Termux.
Chatea, busca archivos, renombra y ejecuta comandos básicos.

Uso:
    python3 asistente.py                    # modo chat interactivo
    python3 asistente.py buscar <texto>     # buscar archivos
    python3 asistente.py listar [ruta]      # listar directorio
    python3 asistente.py renombrar <viejo> <nuevo>
    python3 asistente.py version
"""

import os
import sys
import glob
import shutil
import subprocess
import json

VERSION = "1.0.0"
HIST_DIR = os.path.expanduser("~/.asistente_terminal")
HIST_FILE = os.path.join(HIST_DIR, "historial.json")

# ── Colores para terminal ──────────────────────────────────────
class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    RED    = "\033[31m"
    DIM    = "\033[2m"

def colorizar(texto, color):
    return f"{color}{texto}{C.RESET}"


# ── Funciones de archivo ───────────────────────────────────────
def buscar(patron, ruta=os.getcwd()):
    """Busca archivos que coincidan con el patrón."""
    patron_completo = os.path.join(ruta, f"**/*{patron}*")
    resultados = glob.glob(patron_completo, recursive=True)
    return resultados[:50]  # máximo 50 resultados


def listar(ruta="."):
    """Lista archivos del directorio."""
    ruta = os.path.expanduser(ruta)
    if not os.path.isdir(ruta):
        return [f"No existe: {ruta}"]
    items = []
    for e in sorted(os.listdir(ruta)):
        ruta_completa = os.path.join(ruta, e)
        if os.path.isdir(ruta_completa):
            items.append(f"📁 {e}/")
        else:
            tam = os.path.getsize(ruta_completa)
            if tam > 1048576:
                tam_str = f"{tam/1048576:.1f}MB"
            elif tam > 1024:
                tam_str = f"{tam/1024:.1f}KB"
            else:
                tam_str = f"{tam}B"
            items.append(f"📄 {e}  ({tam_str})")
    return items


def renombrar(viejo, nuevo):
    """Renombra un archivo o directorio."""
    viejo = os.path.expanduser(viejo)
    nuevo = os.path.expanduser(nuevo)
    if not os.path.exists(viejo):
        return False, f"No existe: {viejo}"
    if os.path.exists(nuevo):
        return False, f"Ya existe: {nuevo}"
    shutil.move(viejo, nuevo)
    return True, f"Renombrado: {viejo} → {nuevo}"


def ejecutar_comando(cmd):
    """Ejecuta un comando del sistema."""
    try:
        resultado = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        salida = resultado.stdout.strip()
        error = resultado.stderr.strip()
        if resultado.returncode != 0 and error:
            return False, error
        return True, salida or "(sin salida)"
    except subprocess.TimeoutExpired:
        return False, "Comando expiró (30s)"
    except Exception as e:
        return False, str(e)


# ── Historial ──────────────────────────────────────────────────
def cargar_historial():
    try:
        with open(HIST_FILE) as f:
            return json.load(f)
    except:
        return []


def guardar_historial(historial):
    os.makedirs(HIST_DIR, exist_ok=True)
    with open(HIST_FILE, "w") as f:
        json.dump(historial[-50:], f, ensure_ascii=False, indent=2)


# ── Motor de respuestas (sin LLM, reglas) ─────────────────────
def procesar(texto, cwd):
    """Procesa la entrada del usuario y devuelve (respuesta, acciones)."""
    t = texto.lower().strip()
    acciones = []

    # Salir
    if t in ("salir", "exit", "quit", "cerrar", "adiós", "adios"):
        return "¡Hasta luego!", acciones

    # Ayuda
    if t in ("ayuda", "help", "comandos", "?"):
        acciones.append("ayuda")
        return "ayuda", acciones

    # Versión
    if t in ("version", "versión", "info"):
        return f"Asistente Terminal v{VERSION}", acciones

    # Buscar archivos
    if t.startswith(("buscar ", "busca ", "encuentra ", "find ")):
        patron = texto.split(None, 1)[1] if len(texto.split(None, 1)) > 1 else ""
        if not patron:
            return "¿Qué quieres buscar? Ejemplo: buscar archivo.txt", acciones
        resultados = buscar(patron, cwd)
        acciones.append(f"buscar:{patron}:{len(resultados)}")
        if resultados:
            return f"Encontré {len(resultados)} resultado(s) para '{patron}':\n" + "\n".join(resultados[:15]), acciones
        return f"No encontré nada con '{patron}' en {cwd}", acciones

    # Listar directorio
    if t.startswith(("listar ", "lista ", "ls", "ver archivos")):
        partes = texto.split(None, 1)
        ruta = partes[1] if len(partes) > 1 else "."
        items = listar(ruta)
        acciones.append(f"listar:{ruta}:{len(items)}")
        if items:
            return f"Contenido de {ruta}:\n" + "\n".join(items[:30]), acciones
        return f"Directorio vacío: {ruta}", acciones

    # Renombrar
    if t.startswith(("renombrar ", "rename ")):
        partes = texto.split()
        if len(partes) < 3:
            return "Uso: renombrar archivo_viejo archivo_nuevo", acciones
        ok, msg = renombrar(partes[1], partes[2])
        acciones.append(f"renombrar:{partes[1]}->{partes[2]}:{'ok' if ok else 'error'}")
        return msg, acciones

    # Comando del sistema
    if t.startswith(("ejecuta ", "ejecutar ", "run ", "cmd ")):
        cmd = texto.split(None, 1)[1] if len(texto.split(None, 1)) > 1 else ""
        if not cmd:
            return "¿Qué comando quieres ejecutar? Ejemplo: ejecuta df -h", acciones
        ok, salida = ejecutar_comando(cmd)
        acciones.append(f"ejecutar:{cmd[:50]}:{'ok' if ok else 'error'}")
        return salida, acciones

    # Info del sistema
    if t in ("sistema", "info sistema", "estado", "status"):
        ok, salida = ejecutar_comando("uname -a")
        acciones.append("info_sistema")
        return salida, acciones

    # Directorio actual
    if t in ("dónde estoy", "donde estoy", "cwd", "pwd"):
        return f"Estás en: {cwd}", acciones

    # Hora
    if t in ("hora", "qué hora es", "que hora es", "time"):
        ok, salida = ejecutar_comando("date '+%H:%M:%S %d/%m/%Y'")
        return salida, acciones

    # Responder con ayuda contextual
    return _respuesta_general(t), acciones


def _respuesta_general(texto):
    """Respuesta por defecto cuando no se reconoce la intención."""
    sugerencias = [
        "buscar <archivo>      → Busca archivos en el directorio actual",
        "listar [ruta]         → Lista archivos",
        "renombrar <viejo> <nuevo>  → Renombra un archivo",
        "ejecuta <comando>     → Ejecuta un comando del sistema",
        "sistema               → Info del sistema",
        "dónde estoy           → Directorio actual",
        "hora                  → Hora actual",
        "ayuda                 → Esta lista",
        "salir                 → Cierra el asistente",
    ]
    return "No entendí eso.\n\nComandos disponibles:\n" + "\n".join(sugerencias)


def mostrar_ayuda():
    print(colorizar("\n╔══════════════════════════════════════╗", C.CYAN))
    print(colorizar("║   Asistente Terminal v" + VERSION + "            ║", C.CYAN))
    print(colorizar("╚══════════════════════════════════════╝", C.CYAN))
    print(f"""
{colorizar('Comandos:', C.BOLD)}

  {colorizar('buscar <patrón>', C.GREEN)}       Busca archivos
  {colorizar('listar [ruta]', C.GREEN)}         Lista archivos
  {colorizar('renombrar <viejo> <nuevo>', C.GREEN)}  Renombra archivo
  {colorizar('ejecuta <comando>', C.GREEN)}     Ejecuta comando
  {colorizar('sistema', C.GREEN)}               Info del sistema
  {colorizar('dónde estoy', C.GREEN)}           Directorio actual
  {colorizar('hora', C.GREEN)}                  Hora actual
  {colorizar('ayuda', C.GREEN)}                 Esta lista
  {colorizar('salir', C.GREEN)}                 Cierra

{colorizar('También puedes escribir texto libre.', C.DIM)}
{colorizar('El asistente intentará ayudarte.', C.DIM)}
""")


# ── Modo chat interactivo ──────────────────────────────────────
def chat():
    cwd = os.getcwd()
    mostrar_ayuda()
    historial = cargar_historial()

    while True:
        try:
            entrada = input(colorizar("\n❯ ", C.CYAN)).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n¡Hasta luego!")
            break

        if not entrada:
            continue

        respuesta, acciones = procesar(entrada, cwd)

        if respuesta == "ayuda":
            mostrar_ayuda()
        elif respuesta == "¡Hasta luego!":
            print(colorizar(respuesta, C.GREEN))
            break
        else:
            print(colorizar(respuesta, C.YELLOW))

        historial.append({"entrada": entrada, "respuesta": respuesta[:200]})

    guardar_historial(historial)


# ── CLI directo ────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if not args:
        chat()
        return

    cmd = args[0].lower()

    if cmd == "version":
        print(f"asistente_terminal v{VERSION}")
    elif cmd == "ayuda":
        mostrar_ayuda()
    elif cmd == "buscar" and len(args) > 1:
        resultados = buscar(" ".join(args[1:]))
        for r in resultados:
            print(r)
        if not resultados:
            print("Sin resultados.")
    elif cmd == "listar":
        ruta = args[1] if len(args) > 1 else "."
        for item in listar(ruta):
            print(item)
    elif cmd == "renombrar" and len(args) > 2:
        ok, msg = renombrar(args[1], args[2])
        print(msg)
        sys.exit(0 if ok else 1)
    elif cmd == "ejecuta" and len(args) > 1:
        ok, salida = ejecutar_comando(" ".join(args[1:]))
        print(salida)
        sys.exit(0 if ok else 1)
    elif cmd == "sistema":
        ok, salida = ejecutar_comando("uname -a")
        print(salida)
    elif cmd in ("pwd", "dónde estoy", "donde estoy"):
        print(os.getcwd())
    elif cmd in ("hora", "time"):
        ok, salida = ejecutar_comando("date '+%H:%M:%S %d/%m/%Y'")
        print(salida)
    else:
        print("Comando no reconocido. Usa: asistente.py ayuda")
        sys.exit(1)


if __name__ == "__main__":
    main()
