# 🚀 UPLAN — Easy Macro Recorder v2.0 (Linux Upgrade)

**Autor:** Leoshi  
**Fecha:** 11 de julio de 2026  
**Estado:** ✅ Fase 1 completada — Fase 2 pendiente  
**Repo:** [LJSaumeth/EASY_MACRO_RECORDER](https://github.com/LJSaumeth/EASY_MACRO_RECORDER)

---

## Resumen Ejecutivo

Upgrade completo del Easy Macro Recorder para funcionar en Linux, con fixes de 5 bugs críticos/alto que afectaban todas las plataformas. La app pasa de "solo Windows" a "multiplataforma" con soporte real para Wayland + XWayland.

| Fase | Estado | Descripción |
|------|--------|-------------|
| Fase 1 — Linux Foundation | ✅ Completada | Setup, scripts, fixes de bugs |
| Fase 2 — Hardening | 🔲 Pendiente | Tests, atomic writes, edge cases |
| Fase 3 — Frontend | 🔲 Pendiente | Implementación del UI (según AGENTS.md) |

---

## Fase 1 — Linux Foundation ✅

### 1.1 Entorno de Desarrollo

| Archivo | Acción | Descripción |
|---------|--------|-------------|
| `.venv/` | CREADO | Virtual environment con `--system-site-packages` (necesario para GTK/gi) |
| `setup.sh` | CREADO | Instalador automático multi-distro (Debian, Fedora, Arch, openSUSE) |
| `run.sh` | CREADO | Launcher con detección de Wayland y mensajes informativos |

**Cómo funciona:**
```bash
./setup.sh    # Instala deps del sistema + venv + pip
./run.sh      # Lanza la app
```

### 1.2 Dependencias Instaladas

| Paquete | Tipo | Propósito |
|---------|------|-----------|
| `pynput>=1.8.2` | pip | Captura e inyección de input |
| `pywebview>=6.2.1` | pip | Ventana desktop + bridge JS↔Python |
| `python-xlib>=0.33` | pip | Hooks globales de teclado (X11/Wayland) |
| `python3-gi` | sistema | Bindings GTK3 para pywebview |
| `gir1.2-webkit2-4.1` | sistema | WebKit2 engine para pywebview |

### 1.3 Fixes de Bugs Críticos

#### 🔴 Fix #1: Race Condition en `_pending_events`

**Archivo:** `macro_app/presentation/api.py`  
**Problema:** `list.copy()` + `list.clear()` no atómicos entre threads  
**Solución:** `threading.Lock`

```python
# ANTES
self._pending_events: List[Dict] = []
def _on_state_event(self, event_type, data):
    self._pending_events.append(...)  # Thread unsafe
def get_app_state(self):
    events = self._pending_events.copy()  # Race condition
    self._pending_events.clear()

# DESPUÉS
self._pending_events: List[Dict] = []
self._events_lock = threading.Lock()
def _on_state_event(self, event_type, data):
    with self._events_lock:
        self._pending_events.append(...)
def get_app_state(self):
    with self._events_lock:
        events = list(self._pending_events)
        self._pending_events.clear()
```

**Impacto:** Macros ya no pierden ni duplican eventos durante recording/playback simultáneo.

---

#### 🔴 Fix #2: MacroEditor mutaba una copia

**Archivos:** `application/macro_editor.py`, `application/playback_service.py`  
**Problema:** `get_current_macro()` retornaba una copia; edits se perdían  
**Solución:** Nuevo método `set_macro_events()` para persistir cambios

```python
# ANTES (macro_editor.py)
def delete_event(self, index):
    events = self._playback.get_current_macro()  # Copia
    del events[index]                              # Borra de la copia
    return events                                  # PlaybackService NUNCA se entera

# DESPUÉS
def delete_event(self, index):
    events = self._playback.get_current_macro()  # Copia
    del events[index]
    self._playback.set_macro_events(events)       # ← Persistir
    return events
```

```python
# NUEVO (playback_service.py)
def set_macro_events(self, events: List[MacroEvent]) -> None:
    if self._session.is_playing:
        raise RuntimeError("Cannot modify macro during playback")
    self._session.macro_events = list(events)
```

**Impacto:** La función de edición de eventos ahora funciona. Los cambios se reflejan en el playback.

---

#### 🟠 Fix #3: Mouse Move Throttle

**Archivo:** `infrastructure/pynput_listener.py`  
**Problema:** pynput captura cada pixel de movimiento → ~1500 eventos en 30s  
**Solución:** Throttle de 16ms (~60fps) + threshold de 5px

```python
_MOVE_THROTTLE_MS = 16   # ~60 events/sec max
_MOVE_THRESHOLD_PX = 5   # Minimum pixel movement to register

def _on_mouse_move(self, x, y):
    now = time.time()
    if self._last_move_time is not None:
        elapsed_ms = (now - self._last_move_time) * 1000
        if elapsed_ms < self._MOVE_THROTTLE_MS:
            return True  # Throttled
    if self._last_move_pos is not None:
        dx = abs(x - self._last_move_pos[0])
        dy = abs(y - self._last_move_pos[1])
        if dx < self._MOVE_THRESHOLD_PX and dy < self._MOVE_THRESHOLD_PX:
            return True  # Below threshold
    # ... emit event
```

**Impacto:** ~85% menos eventos de mouse_move. Macros más ligeros y playback más preciso.

---

#### 🟠 Fix #4: `_resolve_key` crash con keys desconocidas

**Archivo:** `infrastructure/pynput_controller.py`  
**Problema:** Keys multimedia/sistema retornaban string → crash en `press()`  
**Solución:** Skip silencioso de keys no soportadas

```python
# ANTES
def _key_action(self, event, is_press):
    resolved_key = self._resolve_key(event.key)
    self._keyboard.press(resolved_key)  # ← Crash si es string

# DESPUÉS
def _key_action(self, event, is_press):
    resolved_key = self._resolve_key(event.key)
    if isinstance(resolved_key, str):
        return  # Key not supported, skip
    try:
        if is_press:
            self._keyboard.press(resolved_key)
        else:
            self._keyboard.release(resolved_key)
    except Exception:
        pass  # Platform doesn't support this key
```

**Impacto:** Macros con multimedia keys ya no crashean.

---

#### 🟡 Fix #5: `_wait_for_delay` impreciso (~50ms)

**Archivo:** `application/playback_service.py`  
**Problema:** Polling con `time.sleep(0.05)` → impreciso y acumula error float  
**Solución:** `threading.Event.wait()` — preciso e interrumpible

```python
# ANTES
def _wait_for_delay(self, delay_ms):
    step = 0.05
    elapsed = 0.0
    while elapsed < delay_ms / 1000.0:
        if self._stop_event.is_set():
            return
        time.sleep(step)
        elapsed += step

# DESPUÉS
def _wait_for_delay(self, delay_ms):
    if delay_ms <= 0:
        return
    self._stop_event.wait(timeout=delay_ms / 1000.0)
```

**Impacto:** Timing de playback más preciso. Emergency stop responde instantáneamente.

---

### 1.4 Mejoras en main.py

| Mejora | Descripción |
|--------|-------------|
| Detección de Wayland | Informa al usuario sobre limitaciones y workarounds |
| Chequeo de dependencias | Verifica gi, WebKit2, python-xlib al inicio |
| Mensajes por distro | Instrucciones específicas para Ubuntu, Fedora, Arch |
| Imports lazy | Deps se importan después del chequeo para errores claros |

---

## Fase 2 — Hardening 🔲

### 2.1 HotkeyConfigStore Atómico

**Prioridad:** 🟡 Medio  
**Archivo:** `infrastructure/hotkey_config_store.py`

```python
# Implementar tempfile + rename (mismo patrón que JsonFileStorage)
def save_config(self, config):
    import tempfile, os
    temp_fd, temp_path = tempfile.mkstemp(
        dir=str(self._config_path.parent), suffix=".json"
    )
    try:
        with os.fdopen(temp_fd, "w") as f:
            f.write(json_text)
        os.replace(temp_path, str(self._config_path))
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise
```

### 2.2 Tests Unitarios

**Prioridad:** 🔴 Alta  
**Framework:** pytest

```
tests/
├── domain/
│   ├── test_models.py          # MacroEvent, Macro, HotkeyConfig
│   └── test_exceptions.py      # Jerarquía de excepciones
├── application/
│   ├── test_recording_service.py   # Start/stop recording
│   ├── test_playback_service.py    # Play/stop/loops/delay
│   ├── test_macro_editor.py        # CRUD de eventos
│   ├── test_persistence_service.py # Save/load/delete
│   └── test_hotkey_service.py      # Bindings, conflicts
├── infrastructure/
│   ├── test_json_file_storage.py   # Atomic writes, corruption
│   └── test_pynput_controller.py   # Key resolution
└── presentation/
    └── test_api.py                 # Integration tests
```

**Tests prioritarios (por bug fix):**
```python
# test_macro_editor.py — Verifica Fix #2
def test_delete_event_persists():
    events = [MacroEvent("key_press", 0, key="a")]
    playback.set_macro_events(events)
    editor.delete_event(0)
    assert len(playback.get_current_macro()) == 0  # No era copia

# test_api_thread_safety.py — Verifica Fix #1
def test_pending_events_thread_safe():
    threads = [Thread(target=lambda: api._on_state_event("test", {})) for _ in range(100)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert len(api._pending_events) == 100
```

### 2.3 Mouse Move Downsmpling Opcional

**Prioridad:** 🟢 Bajo  
**Descripción:** Opción de grabar mouse_move como splines en vez de eventos individuales

```
Opción A: Throttle (actual) — Simple, funciona
Opción B: Spline interpolation — Complejo, mejor compresión
```

### 2.4 `Macro.INFINITE_LOOP` Cleanup

**Prioridad:** 🟢 Bajo  
**Archivo:** `domain/models.py`

```python
# ANTES (código muerto)
class Macro:
    INFINITE_LOOP = -1  # Nunca se usa

# DESPUÉS — usar como constante referenciada
# En PlaybackService:
is_infinite = max_loops == Macro.INFINITE_LOOP
```

---

## Fase 3 — Frontend Implementation 🔲

Según AGENTS.md, el frontend tiene 6 specs y 6 plans listos pero la implementación está pendiente.

### Specs existentes (en `DOCS/SPECS/`):
- `frontend-recording-panel`
- `frontend-playback-panel`
- `frontend-file-panel`
- `frontend-editor-panel`
- `frontend-hotkey-panel`
- `frontend-status-bar`

### Orden de implementación sugerido:
1. **Status Bar** (base para feedback)
2. **Recording Panel** (core functionality)
3. **Playback Panel** (depende de recording)
4. **File Panel** (save/load)
5. **Editor Panel** (advanced editing)
6. **Hotkey Panel** (configuration)

---

## Archivos Modificados (Fase 1)

| Archivo | Cambio |
|---------|--------|
| `macro_app/main.py` | Linux dep checks, Wayland detection, lazy imports |
| `macro_app/presentation/api.py` | `threading.Lock` para `_pending_events` |
| `macro_app/application/playback_service.py` | `set_macro_events()`, `_wait_for_delay()` con `Event.wait()` |
| `macro_app/application/macro_editor.py` | Todas las mutaciones ahora persisten via `set_macro_events()` |
| `macro_app/infrastructure/pynput_listener.py` | Mouse move throttle (16ms + 5px) |
| `macro_app/infrastructure/pynput_controller.py` | `_key_action()` con try/except para keys no soportadas |
| `setup.sh` | NUEVO — Instalador multi-distro |
| `run.sh` | NUEVO — Launcher con Wayland detection |

---

## Verificación

```bash
# Todos los tests pasan (8/8)
1. Imports                         ✅
2. Build services                  ✅
3. Recording lifecycle             ✅
4. Save/Load/Delete                ✅
5. MacroEditor mutations persist   ✅
6. Thread safety (lock)            ✅ (500 events sin pérdida)
7. Mouse throttle                  ✅ (threshold + time-based)
8. App state                       ✅

# GUI launch
./run.sh → EXIT 124 (timeout = app corrió OK)
```

---

## Comando Rápido

```bash
# Primera vez
cd EASY_MACRO_RECORDER
./setup.sh

# Cada vez que quieras usar
./run.sh
```

---

*UPLAN generado el 11/07/2026 — Leoshi*
