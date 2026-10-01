# Guía de uso de uv

Guía de referencia rápida para gestionar proyectos Python con [uv](https://docs.astral.sh/uv/). Los ejemplos de terminal usan PowerShell (Windows); en Linux/macOS los comandos de uv son idénticos.

> Nota: los comandos corresponden a la interfaz estable de uv. Si alguno falla o cambia, `uv <comando> --help` y la documentación oficial son la referencia definitiva.

---

## 1. Instalación y mantenimiento de uv

### Instalar

```powershell
# Windows (instalador oficial)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Windows (alternativa con winget)
winget install --id=astral-sh.uv -e
```

```bash
# Linux / macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verificar y actualizar

```bash
uv --version          # verifica la instalación
uv self update        # actualiza uv (solo si se instaló con el instalador oficial)
```

Si uv se instaló con winget, pip u otro gestor, se actualiza con ese mismo gestor.

### Autocompletado (opcional)

```powershell
# PowerShell: agregar al perfil ($PROFILE)
(& uv generate-shell-completion powershell) | Out-String | Invoke-Expression
```

---

## 2. Iniciar un proyecto nuevo

```bash
uv init mi-proyecto            # crea carpeta nueva con el proyecto
cd mi-proyecto
```

Variantes:

| Comando                 | Resultado                                            |
| ----------------------- | ---------------------------------------------------- |
| `uv init`               | Inicializa el proyecto en la carpeta actual          |
| `uv init --app`         | Aplicación (valor por defecto)                       |
| `uv init --lib`         | Librería con estructura `src/`                       |
| `uv init --package`     | Aplicación empaquetada con `src/` y punto de entrada |
| `uv init --python 3.12` | Fija la versión de Python del proyecto               |
| `uv init --no-readme`   | Sin README                                           |

Archivos que crea: `pyproject.toml`, `.python-version`, `README.md`, `main.py` (o `src/`), y un repositorio git si no existe.

Después de agregar la primera dependencia se generan además:

- `uv.lock`: versiones exactas resueltas (se versiona en git).
- `.venv/`: entorno virtual (no se versiona).

### Flujo típico completo

```bash
uv init qr-app --python 3.12
cd qr-app
uv add qrcode[pil] customtkinter pillow     # dependencias del proyecto
uv add --dev ruff pytest                    # dependencias de desarrollo
uv run main.py                              # ejecutar
```

---

## 3. Trabajar en un proyecto ya creado

Caso: clonaste el repositorio o volviste a una carpeta existente.

```bash
git clone <url-del-repo>
cd <carpeta>
uv sync               # crea .venv, instala Python si hace falta y las dependencias del lock
uv run main.py        # ejecuta (también sincroniza automáticamente)
```

Notas:

- `uv sync` instala también el grupo `dev` por defecto.
- `uv sync --no-dev` omite dependencias de desarrollo.
- `uv sync --locked` falla si `uv.lock` no coincide con `pyproject.toml` (útil en CI).
- `uv sync --frozen` usa el lock tal cual, sin verificarlo ni actualizarlo.
- No necesitas activar el entorno: `uv run` lo usa directamente.

### Activar el entorno manualmente (opcional)

```powershell
.venv\Scripts\Activate.ps1      # Windows PowerShell
```
```bash
source .venv/bin/activate       # Linux / macOS
deactivate                      # salir
```

Si PowerShell bloquea el script:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

---

## 4. Gestión de dependencias

| Acción                       | Comando                                                |
| ---------------------------- | ------------------------------------------------------ |
| Agregar paquete              | `uv add requests`                                      |
| Agregar con versión          | `uv add "requests>=2.31,<3"`                           |
| Agregar con extras           | `uv add "qrcode[pil]"`                                 |
| Agregar solo para desarrollo | `uv add --dev pytest`                                  |
| Agregar a un grupo propio    | `uv add --group docs mkdocs`                           |
| Agregar desde git            | `uv add git+https://github.com/usuario/repo`           |
| Importar desde requirements  | `uv add -r requirements.txt`                           |
| Quitar paquete               | `uv remove requests`                                   |
| Ver árbol de dependencias    | `uv tree`                                              |
| Actualizar un paquete        | `uv lock --upgrade-package requests` y luego `uv sync` |
| Actualizar todo              | `uv lock --upgrade` y luego `uv sync`                  |
| Regenerar lock sin instalar  | `uv lock`                                              |
| Exportar a requirements.txt  | `uv export --no-hashes -o requirements.txt`            |

Regla práctica: usa siempre `uv add` / `uv remove` en lugar de editar `pyproject.toml` a mano; así el lock y el entorno quedan consistentes.

---

## 5. Ejecutar código

```bash
uv run main.py                     # script
uv run python -m paquete.modulo    # módulo (p. ej. uv run python -m src.main)
uv run pytest                      # herramienta instalada en el proyecto
uv run ruff check .                # linter
uv run python                      # intérprete con el entorno del proyecto
uv run --with rich main.py         # agrega un paquete temporal solo para esta ejecución
uv run --no-sync main.py           # ejecuta sin sincronizar el entorno antes
```

---

## 6. Versiones de Python

```bash
uv python list                  # versiones disponibles e instaladas
uv python install 3.12          # descarga e instala una versión
uv python install 3.11 3.12     # varias a la vez
uv python uninstall 3.11        # desinstala
uv python pin 3.12              # escribe .python-version en el proyecto
uv python find                  # muestra cuál usaría uv
uv venv --python 3.12           # crea .venv con esa versión
```

Para cambiar la versión de un proyecto existente:

1. `uv python pin 3.13`
2. Ajustar `requires-python` en `pyproject.toml` si es necesario.
3. `rm -r .venv` (o `Remove-Item -Recurse -Force .venv`) y luego `uv sync`.

---

## 7. Scripts sueltos (sin proyecto)

```bash
uv init --script utilidad.py --python 3.12     # crea script con metadatos en línea
uv add --script utilidad.py requests rich      # agrega dependencias al script
uv run utilidad.py                             # ejecuta con entorno aislado automático
```

Las dependencias quedan declaradas en un bloque `# /// script` al inicio del archivo.

---

## 8. Herramientas de línea de comandos (uvx / uv tool)

Para utilidades que no son dependencias del proyecto (ruff, black, httpie, etc.).

```bash
uvx ruff check .                 # ejecuta sin instalar (entorno temporal)
uv tool install ruff             # instala de forma persistente
uv tool list                     # lista herramientas instaladas
uv tool upgrade ruff             # actualiza una
uv tool upgrade --all            # actualiza todas
uv tool uninstall ruff           # desinstala
uv tool update-shell             # agrega el directorio de herramientas al PATH
```

`uvx` es un alias de `uv tool run`.

---

## 9. Comandos más usados (resumen)

| Necesidad                         | Comando                         |
| --------------------------------- | ------------------------------- |
| Crear proyecto                    | `uv init nombre`                |
| Instalar todo lo del proyecto     | `uv sync`                       |
| Agregar dependencia               | `uv add paquete`                |
| Agregar dependencia de desarrollo | `uv add --dev paquete`          |
| Quitar dependencia                | `uv remove paquete`             |
| Ejecutar script                   | `uv run archivo.py`             |
| Ver dependencias                  | `uv tree`                       |
| Actualizar dependencias           | `uv lock --upgrade` + `uv sync` |
| Instalar Python                   | `uv python install 3.12`        |
| Ejecutar herramienta puntual      | `uvx herramienta`               |
| Limpiar caché                     | `uv cache clean`                |
| Ayuda de un comando               | `uv <comando> --help`           |

---

## 10. Interfaz compatible con pip

Para entornos que no son un proyecto uv (migraciones, scripts de despliegue):

```bash
uv venv                               # crea .venv
uv pip install requests               # instala en el entorno activo/.venv
uv pip install -r requirements.txt
uv pip list
uv pip freeze > requirements.txt
uv pip uninstall requests
uv pip compile requirements.in -o requirements.txt
```

En un proyecto con `pyproject.toml` se recomienda `uv add`, no `uv pip install`, porque este último no actualiza `pyproject.toml` ni `uv.lock`.

---

## 11. Manejo de errores frecuentes

### `No pyproject.toml found in current directory`
Estás en una carpeta equivocada o el proyecto no se inicializó.
Solución: `cd` a la raíz del proyecto, o ejecutar `uv init`.

### `ModuleNotFoundError` al ejecutar
El paquete no está instalado en el entorno del proyecto o ejecutaste con otro Python.
Solución: `uv add paquete` o `uv sync`, y ejecutar con `uv run` (no con `python` directamente).

### `ModuleNotFoundError: No module named 'src'`
Se ejecutó un archivo dentro de `src/` directamente, lo que rompe los imports absolutos.
Solución: ejecutar desde la raíz como módulo: `uv run python -m src.main` (ajustar al nombre real del módulo de entrada).

### `No module named 'tkinter'` / `_tkinter`
- Con Python administrado por uv en Windows/macOS normalmente viene incluido.
- Con Python del sistema en Linux: instalar `python3-tk` (Debian/Ubuntu: `sudo apt install python3-tk`).
- Alternativa: `uv python install 3.12` para usar un Python administrado por uv.

### El lock está desactualizado (`--locked` falla)
`pyproject.toml` cambió sin regenerar `uv.lock`.
Solución: `uv lock` y luego `uv sync`.

### Conflicto de resolución de dependencias
uv no encuentra versiones compatibles.
Pasos: leer el mensaje (indica qué paquetes chocan), relajar la restricción de versión en `pyproject.toml`, verificar `requires-python`, y ejecutar `uv lock` de nuevo.

### `Failed to hardlink files; falling back to full copy`
La caché y el proyecto están en discos o sistemas de archivos distintos. Es solo una advertencia.
Silenciar: `$env:UV_LINK_MODE = "copy"` (PowerShell) o `export UV_LINK_MODE=copy`.

### `Access is denied` / archivo en uso al sincronizar (Windows)
Un proceso (la app en ejecución, el IDE, antivirus) mantiene bloqueado algo de `.venv`.
Solución: cerrar la app y terminales que usen el entorno, reintentar `uv sync`; si persiste, borrar `.venv` y sincronizar de nuevo.

### El entorno quedó corrupto o extraño
```powershell
Remove-Item -Recurse -Force .venv
uv sync
```
Es seguro: `.venv` se regenera completo desde `uv.lock`.

### Errores de red, proxy o certificados
- Probar con `--native-tls` (usa los certificados del sistema): `uv sync --native-tls`.
- Proxy corporativo: definir `HTTPS_PROXY` / `HTTP_PROXY`.
- Reintentar con más tiempo: `$env:UV_HTTP_TIMEOUT = "120"`.

### `uv` no se reconoce como comando
El directorio de instalación no está en el `PATH`.
Solución: cerrar y abrir la terminal; si persiste, ejecutar `uv tool update-shell` o reinstalar uv.

### Caché con problemas
```bash
uv cache clean          # borra toda la caché
uv cache prune          # elimina solo entradas sin uso
uv cache dir            # muestra dónde está
```

### Diagnóstico general
```bash
uv sync -v              # salida detallada
uv sync -vv             # más detalle aún
uv run --no-cache main.py
```

---

## 12. Buenas prácticas

- Versionar en git: `pyproject.toml`, `uv.lock`, `.python-version`.
- No versionar: `.venv/` (agregar a `.gitignore`).
- Usar siempre `uv add` / `uv remove` para modificar dependencias.
- Separar dependencias de desarrollo con `--dev`.
- Ejecutar con `uv run` para no depender de activar el entorno.
- En CI o despliegue: `uv sync --locked` para reproducibilidad exacta.
- Antes de actualizar todo, confirmar que el proyecto funciona y hacer commit; así el cambio de `uv.lock` es fácil de revertir.

---

## 13. Empaquetado y publicación (referencia)

```bash
uv build                       # genera wheel y sdist en dist/
uv publish                     # publica en PyPI (requiere token)
uv version                     # muestra la versión del proyecto
uv version --bump minor        # incrementa la versión (según versión de uv instalada)
```

Para generar un ejecutable de una app de escritorio (como una GUI con customtkinter) se usa una herramienta adicional, por ejemplo PyInstaller: `uv add --dev pyinstaller` y luego `uv run pyinstaller ...`.

---

## Referencias

- Documentación oficial de uv: https://docs.astral.sh/uv/
- Referencia de comandos (CLI): https://docs.astral.sh/uv/reference/cli/
- Guía de proyectos: https://docs.astral.sh/uv/guides/projects/
- Variables de entorno: https://docs.astral.sh/uv/reference/environment/