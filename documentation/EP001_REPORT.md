# Отчёт EP-001 — «Бип и красный мячик»

## Статус

Собран полноценный Godot 4 проект серии с автоматическим экспортом Movie Maker → FFmpeg. Финальный MP4: `godot_project/output/BIP_EP001_FINAL.mp4` (после успешного `./scripts/build_episode.sh FINAL`).

## Что сделано

- Godot 4.4 проект без игрового UI/механик
- Персонаж Бип на базе Quaternius Animated Robot (CC0) + цвет/антенна/масштаб
- Комната Soft Toy + мебель Kenney + реквизит (мяч, корзина, кубики, кресло)
- Детерминированный таймлайн 18 кадров / 180 с (`EpisodeDirector.gd`)
- Русская озвучка диктора и Бипа
- Оригинальная мягкая музыка и SFX
- PREVIEW и FINAL сборка через `scripts/build_episode.sh`
- Документация лицензий и повторного рендера

## 3D-модели и источники

| Модель | URL | Лицензия |
|--------|-----|----------|
| Quaternius Animated Robot | https://poly.pizza/m/QCm7qe9uNJ | CC0 |
| Kenney Furniture Kit | https://kenney.nl/assets/furniture-kit | CC0 |
| Room / ball / basket / chair / blocks | Blender, проект Mult | оригинал |

## TTS

- Диктор: Edge TTS `ru-RU-DmitryNeural` (часть реплик) + eSpeak-NG ru fallback
- Бип: eSpeak-NG ru + FFmpeg pitch/echo (дружелюбный «электронный» оттенок)

## Проверки

| Проверка | Результат |
|----------|-----------|
| Бип — полноценная 3D-модель (не примитив-капсула) | Да (Quaternius + адаптация) |
| GLB загружаются | Да |
| 18 кадров таймлайна | Да |
| Movie Maker 30 FPS | Да (PREVIEW пройден) |
| Аудиодорожка AAC | Да (mux FFmpeg) |
| PREVIEW 12 с 1280×720 | Пройден |
| FINAL 180 с 1080p | См. лог `output/final_build.log` / ffprobe |

## Как повторить рендер

```bash
./scripts/build_episode.sh FINAL
```

Подробности: `documentation/RENDERING.md`.

## Ограничения среды

- Рендер на CPU (llvmpipe), без дискретного GPU — FULL занимает порядка нескольких минут.
- Edge TTS нестабилен по сети → часть дикторских реплик через eSpeak-NG.
- Аудио Movie Maker не используется как источник истины; синхронизация через master WAV + FFmpeg.

## Где лежит MP4

`godot_project/output/BIP_EP001_FINAL.mp4`
