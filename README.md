# Бип и его открытия

Детский 3D-мультсериал (1–3 года). Движок: **Godot 4.4**.

## Серия 1 — «Бип и красный мячик»

- Длительность: **180 секунд**
- Формат: **1920×1080**, 30 FPS, MP4 (H.264 + AAC)
- Озвучка: русский (диктор + Бип)
- Готовый файл: `godot_project/output/BIP_EP001_FINAL.mp4`

## Быстрый старт

```bash
# Зависимости: Godot 4.4+, FFmpeg, Python 3
export GODOT=/path/to/godot

# Быстрый тест (12 с, 720p)
./scripts/build_episode.sh PREVIEW

# Полная серия (180 с, 1080p)
./scripts/build_episode.sh FINAL
```

Подробности: [`documentation/RENDERING.md`](documentation/RENDERING.md).

## Структура

```
godot_project/
  characters/     # Бип (Quaternius + адаптация)
  locations/      # Комната Бипа
  props/          # Мяч, корзина, мебель, игрушки
  episodes/ep001/ # Таймлайн и режиссёр серии
  audio/          # Речь, музыка, SFX, master WAV
  output/         # MP4 и логи сборки
  screenshots/    # Контрольные кадры
scripts/
  build_episode.sh
documentation/
```

## Документация

| Файл | Содержание |
|------|------------|
| [`documentation/PRODUCTION.md`](documentation/PRODUCTION.md) | Производственный пайплайн |
| [`documentation/RENDERING.md`](documentation/RENDERING.md) | Movie Maker + FFmpeg |
| [`documentation/ASSETS_LICENSES.md`](documentation/ASSETS_LICENSES.md) | Лицензии ассетов |
| [`documentation/EP001_REPORT.md`](documentation/EP001_REPORT.md) | Отчёт по EP-001 |

## Повторное использование

Персонаж Бип и комната рассчитаны на следующие серии: новые эпизоды кладутся в `episodes/ep00N/` с общим `characters/` и `locations/`.
