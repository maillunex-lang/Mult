# Отчёт EP-001 — «Бип и красный мячик»

## Статус: готовый MP4 собран и проверен

Файл: **`godot_project/output/BIP_EP001_FINAL.mp4`**

| Параметр | Значение | Статус |
|----------|----------|--------|
| Длительность | 180.000 с | PASS |
| Разрешение | 1920×1080 | PASS |
| FPS | 30 | PASS |
| Кадры | 5400 | PASS |
| Видео | H.264 | PASS |
| Аудио | AAC | PASS |
| Размер | ~45 МБ | — |

## Что сделано

1. Godot 4.4 проект мультфильма (не игра): сцена, свет, таймлайн 18 кадров.
2. Бип: Quaternius Animated Robot (CC0) + бирюзовый цвет #75D4E8, жёлтая антенна, рост ~65 см, анимации Idle/Walk/Wave/Yes/No и др.
3. Комната Soft Toy + мебель Kenney Furniture Kit (CC0) + мяч/корзина/кресло/кубики.
4. Русская озвучка диктора и Бипа + master WAV 180 с.
5. Автосборка: Godot Movie Maker → FFmpeg → ffprobe (`scripts/build_episode.sh PREVIEW|FINAL`).
6. Скриншоты: `godot_project/screenshots/ep001_{begin,middle,end}.png`.
7. Документация: README, PRODUCTION, RENDERING, ASSETS_LICENSES.

## Источники 3D

| Модель | URL | Лицензия |
|--------|-----|----------|
| Quaternius Animated Robot | https://poly.pizza/m/QCm7qe9uNJ | CC0 |
| Kenney Furniture Kit | https://kenney.nl/assets/furniture-kit | CC0 |
| Room / ball / basket / yellow chair / blocks | Blender, проект | оригинал |

## TTS

- Диктор: Edge TTS `ru-RU-DmitryNeural` + eSpeak-NG (fallback при лимитах API)
- Бип: eSpeak-NG + FFmpeg (pitch/echo)

## Как повторить рендер

```bash
export GODOT=/path/to/godot
./scripts/build_episode.sh FINAL
```

## Оставшиеся улучшения (не блокируют сдачу файла)

- Смягчить тени / подобрать экспозицию под preschool look.
- Доработать стыки стен комнаты (сейчас панели + открытый фронт для камеры).
- При желании заменить eSpeak-реплики полностью на Edge TTS при стабильной сети.
- Более плотный риггинг мимики Бипа (сейчас — скелетные клипы Quaternius + таймлайн).
