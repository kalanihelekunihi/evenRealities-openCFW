# Community Apps

Open-source EvenHub apps from the community, downloaded 2026-03-06 via GitHub code search
for `@evenrealities/even_hub_sdk` usage. Source code is in `third_party/community-apps/`.

## App Catalog

| App | Author | Description |
|-----|--------|-------------|
| arkanoid-even-g2 | nickustinov | Arkanoid/Breakout game |
| books-even-g2 | nickustinov | Book reader |
| epub-reader-g2 | chortya | EPUB reader with chapter navigation |
| even-aozora-reader | howyi | Japanese Aozora Bunko reader |
| even-stars | thibautrey | Star map / astronomy |
| Even-Todoist | wethegreenpeople | Todoist integration |
| even-transit | langerhans | Transit/public transport info |
| even-travel-companion | thibautrey | Travel companion utilities |
| EvenChess | dmyster145 | Chess game |
| EvenRoads | dmyster145 | Road/driving info |
| EvenSmartThings | dmyster145 | SmartThings home automation |
| EvenSolitaire | dmyster145 | Solitaire card game |
| EvenTwitchChat | kevin-huff | Twitch chat overlay |
| EvenWorldClock | KamalQ | World clock display |
| g2-flashcards | tomtau | Flashcard study tool |
| itsyhome-even-g2 | nickustinov | Smart home dashboard |
| pong-even-g2 | nickustinov | Pong game |
| smart-even-g2 | nickustinov | Smart home control |
| smrti | prasants | Meditation/mindfulness timer |
| snake-even-g2 | nickustinov | Snake game |
| stt-even-g2 | nickustinov | Speech-to-text display |
| tesla-even-g2 | nickustinov | Tesla vehicle integration |
| tetris-even-g2 | nickustinov | Tetris game |
| weather-even-g2 | nickustinov | Weather display |

## Notable Implementations

- **even-stars**: Extensive SDK documentation (1183 lines), deep-sky object catalog,
  implementation plan. Good reference for complex EvenHub rendering.
- **g2-flashcards**: Detailed agent workflow documentation (1015 lines).
- **EvenSolitaire**: Full game with canvas rendering, design docs, build plans.
- **epub-reader-g2**: File handling, chapter navigation, text pagination.

## SDK Usage Pattern

All apps use the `@evenrealities/even_hub_sdk` (v0.0.7) package. Some also use:
- `@jappyjan/even-better-sdk` — higher-level page composition API
- `@jappyjan/even-realities-ui` — React UI components for browser-based settings
