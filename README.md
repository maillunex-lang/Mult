# Бип и его открытия

Детский мультсериал.

## EP-002 — «Бип и цветные шарики» (2D, до 2 лет)

Музыкальный развивающий мультик про цвета. **Без озвучки** — крупные русские субтитры снизу.

- 100 с · 1920×1080 · 30 FPS · H.264 + AAC
- Вся графика и анимация сгенерированы в Python (Pillow), без Godot
- Файл: `ep002_2d/output/BIP_EP002_COLORS_FINAL.mp4`

```bash
./scripts/build_ep002_2d.sh
```

Сюжет: [`ep002_2d/docs/EP002_STORY.md`](ep002_2d/docs/EP002_STORY.md)

## EP-001 — «Бип и красный мячик» (3D)

- 180 с · 1080p · русская озвучка
- `godot_project/output/BIP_EP001_FINAL.mp4`
- Сборка: `./scripts/build_episode.sh FINAL`

## Структура

```
ep002_2d/           # 2D серия (Python + FFmpeg)
godot_project/      # 3D серия EP-001
scripts/
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
