# Рендер и сборка MP4

Автоматический пайплайн: **Godot 4 Movie Maker → FFmpeg → ffprobe QA**.

## Единая команда

```bash
export GODOT=/path/to/godot   # по умолчанию ищет godot в PATH
./scripts/build_episode.sh PREVIEW   # 12 с, 1280×720
./scripts/build_episode.sh FINAL     # 180 с, 1920×1080
```

Результат FINAL: `godot_project/output/BIP_EP001_FINAL.mp4`.

## Как это работает

1. **Import** — `godot --headless --import` подготавливает `.godot/imported`.
2. **Movie Maker** — `godot --write-movie … --fixed-fps 30 --quit-after N`:
   - детерминированная шкала времени (кадр = 1/30 с);
   - независимо от скорости GPU;
   - видеоряд без опоры на запись экрана / OBS.
3. **FFmpeg** — склеивает AVI Movie Maker с `audio/master_ep001.wav`:
   - H.264 (`libx264`, CRF 18) + AAC 192k;
   - `yuv420p`, `+faststart` для YouTube.
4. **QA** — `ffprobe` проверяет длительность, разрешение, FPS, наличие звука, число кадров.

## Режимы

| Режим | Длительность | Разрешение | Кадры | Файл |
|-------|--------------|------------|-------|------|
| PREVIEW | 12 с | 1280×720 | 360 | `BIP_EP001_PREVIEW.mp4` |
| FINAL | 180 с | 1920×1080 | 5400 | `BIP_EP001_FINAL.mp4` |

## Аудиосинхронизация

Movie Maker в headless/software-окружении может не записать надёжную аудиодорожку (dummy ALSA). Поэтому:

- видео рендерится Movie Maker’ом;
- полная 180-секундная дорожка заранее собрана в `godot_project/audio/master_ep001.wav` по таймкодам сценария;
- FFmpeg накладывает звук 1:1 по времени.

Пересборка master-аудио: см. `scripts` / блок в `PRODUCTION.md`.

## Повтор для следующих серий

1. Создать `episodes/ep00N/` с режиссёром и таймлайном.
2. Собрать `audio/master_ep00N.wav` (180 с).
3. Добавить режим в `scripts/build_episode.sh` или вызвать Godot/FFmpeg по тому же шаблону.
4. Выход: `output/BIP_EP00N_FINAL.mp4`.

## Типичные проблемы

| Симптом | Решение |
|---------|---------|
| Нет `.avi` после Movie Maker | Проверить DISPLAY / OpenGL (llvmpipe), логи `output/render.log` |
| Чёрный ролик | Ошибка GDScript — смотреть Parse Error в логе |
| Длительность ≠ 180 с | Проверить `--quit-after 5400` и что режиссёр не выходит раньше |
| Нет звука | Убедиться, что `master_ep001.wav` существует и FFmpeg map 1:a |
