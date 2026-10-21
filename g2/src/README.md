# G2 firmware source tree

Every reconstructed G2 C/assembly source lives here, organised by payload. It
merges `g2/components/*`, the C reduced in `g2/analysis/c-source-completion-*`,
and the experimental units `g2/firmware_c` used to compile on 2026-10-21. The
pre-merge layout is preserved at Git tag `pre-consolidation`.

Nothing here is source-complete or byte-identical to stock yet. The tree is
the single place where reconstruction C accumulates; byte identity is decided
per function by `tools/build/qualify_sources.py` and integrated through
`tools/build/source-plan.json` (see [`docs/build.md`](../../docs/build.md)).

```
g2/src/
├── sources.json          every unit: payload, toolchain, compile profile, role, origin
├── include/freestanding  libc shims shared by the bare-metal Apollo builds
├── apollo-common/        Ambiq HAL, FreeRTOS, WSF and audio-port modules used by both Apollo images
├── apollo-bootloader/    Even bootloader (Apollo510, 0x410000)
├── apollo-main/          main application (Apollo510, 0x438000), by subsystem:
│   ├── app/              product services, protobuf handlers, page/UI controllers
│   ├── audio/            PCM pipeline, transitions, encoder setup
│   ├── ble/              Cordio/Packetcraft host deltas, SMP, HCI tables, WSF
│   ├── drivers/          codec host (GX8002 link), display/uLED, flash/MSPI, power, peripherals
│   ├── graphics/         NemaGFX/GPU buffer handlers
│   ├── hal/              clock, UART, GPIO, DMA
│   ├── rtos/             FreeRTOS/CMSIS adaptations
│   ├── runtime/          IAR runtime, TLSF, float, startup
│   ├── storage/          FlashDB, littlefs file layer, tracepoints
│   ├── system/           logging/formatters, platform callbacks, glue aliases
│   ├── ui/               LVGL and FreeType deltas
│   └── include/          headers shared across subsystems
├── case/                 charging-case STM32G0 (0x08000000)
├── touch/                PSoC 4000T touch controller
├── codec/                GX8002 voice codec (image A application, image B SRAM, stage 1)
└── em9305/               EM9305 BLE controller (QP/C scheduler, initializer lowers)
```

Module directories keep the name of the experiment they came from, minus the
`_candidate`, `_offline` and date suffixes. Function names and file names keep
their stock-address suffixes (`_4bfb72`), which are the join key to
[`g2/symbols/`](../symbols/README.md). Subsystem placement under `apollo-main/`
is organisational; the symbol maps remain the authority on what a function is.

## Building

```sh
make sources-check     # every source file is listed once; every unit exists
make sources           # compile every unit, per-payload duplicate check and relocatable
make sources-qualify   # compile and compare anchored functions against the stock payloads
```

`make sources` runs [`tools/build/sources.py`](../../tools/build/sources.py).
It uses host Clang for the ARM payloads and the pinned C-SKY (codec) and ARC
(EM9305) GCC builds in Docker; see `toolchains` in `sources.json` and
`vendor-cache/` in [`docs/build.md`](../../docs/build.md). Output goes to a
fresh `build/sources/` with one `report.json`.

## `sources.json`

| Field | Meaning |
| --- | --- |
| `payload` | link group: `g2-apollo-main`, `g2-apollo-bootloader`, `g2-case`, `g2-touch`, `g2-codec-a`, `g2-codec-b`, `g2-em9305` |
| `toolchain`, `profile` | compiler and the exact flag list the unit compiled with before the merge |
| `role` | `selected` (supplies bytes to the hybrid build), `experimental`, `candidate`, `upstream` (pinned third-party file compiled as part of the payload) |
| `link: false` | compiled and reported, but kept out of the payload relocatable; `note` says why (an alias wrapper `#include`s it, or another unit owns the same symbols) |
| `expect: fails` | a known, pre-existing compile failure, with the first error in `note`; anything else that fails to compile fails the build |
| `origin` | the file's path before the merge (`git show pre-consolidation:<origin>`) |

Where several experiments implemented the same stock function, one copy was
kept: build-selected first, then qualified, then the copy the old per-image
builders linked. Superseded copies were deleted; their history is under
`origin` in the tag.

## Knowledge that used to sit next to the experiments

The reports, closures and reviews in the removed `g2/analysis/` and `reviews/`
trees were distilled into `g2/docs/reference/findings-*.md`. Data files that
tools still read moved to [`g2/evidence/`](../evidence/README.md); behavioural
Unicorn simulators moved to `g2/tests/simulators/`.
