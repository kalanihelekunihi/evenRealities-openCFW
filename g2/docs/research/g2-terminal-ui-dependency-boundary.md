# G2 terminal UI dependency boundary

The two retained-path anchors / 390 bytes expand to ninety-nine functions /
13,200 body bytes for `app\gui\terminal\terminal_ui.c`. The complete physical
object is `[0x005E47CC,0x005E7EA4)`, 14,040 bytes. Ghidra discovered
twenty-three functions; seventy-six source-order routines were restored,
completing the terminal display dispatch, input event routing, screen and
list construction, and the registered callback tables.

## Extent and boundaries

The object opens at `0x005E47CC`, exactly where the closed `terminal.c`
interval `[0x005E42EC,0x005E47CC)` ends; that closure already pins the same
first function (`0x005E47CC`–`0x005E47FE`, sha256 `b3c87d81…`) as its
"following terminal-ui function". The object closes with a 152-byte trailing
literal pool `[0x005E7E0C,0x005E7EA4)` holding the fifth path-pointer cell
`0x005E7E18`. The two following helpers are excluded as the head of the open
`terminal_timer.c` object: `0x005E7EA4` is called only from inside the
timer-tagged body (`0x005E8020`, `0x005E808A`), and `0x005E7EC4` draws its
literal from the timer trailing pool at `0x005E8124`; timer-tag logging
(`terminal_timer.c` path cell `0x005E8130`) starts at `0x005E7ED4`. The one
cross-call from this body into `0x005E7EC4` (site `0x005E7212`) mirrors the
`terminal.c`→`terminal_ui.c` cross-calls and does not extend the object.
Boundary slices of 16 bytes on both sides are hash-pinned.

## Function inventory and noncode

All ninety-nine functions are fully flow-covered with no embedded data.
Thirty-five inter-function/trailing literal pools (840 noncode bytes)
complete the physical object. Two functions are path-anchored (`0x005E4920`,
`0x005E4A6E`); all fifty-five path-pointer literal references across the five
cells (`0x005E547C`, `0x005E6000`, `0x005E6B8C`, `0x005E72B8`, `0x005E7E18`)
land inside the recovered body, proving no further path-logging code hides
in the pools.

## Ingress closure

Ingress is pinned by 197 whole-image direct BL entry sites (34 external to
the physical object) and 135 stored function entry pointers — the input
event and session handler tables that drive this object. There is no
strict-interior ingress. Four raw unaligned BL decodes at `0x005E1CE0`,
`0x005E1CF6`, `0x005E1D16`, `0x005E1D2C` target function interiors; each site
is proven to be the second halfword of the aligned four-byte `mul` at
site−2 inside the unrelated `0x005E1BDE` body, not a real call. One indirect
`blx r2` at `0x005E7CC2` remains an open heap dispatch: `r2` is loaded from
`[r8,#4]` where `r8` derives from a caller-supplied runtime event/session
pointer (terminal.c passes a stack-built event record at `0x005E45AA`), so
the target is written at runtime from registered handler tables rather than
a ROM constant. The candidate suppliers are bounded by the stored-pointer
censuses of `terminal.c`, this object (135), and
`terminal_session_list_ui.c` (25); the site encoding is pinned.

## Provider boundary

All 645 external direct calls terminate at admitted providers: EasyLogger
(275), LVGL (142 across 36 admitted entries, including the `lv_animimage.c`
cluster `0x00597EA6`–`0x00597F52`), bounded IAR DLIB (9: `0x0043C0E4`
copy/fill), CMSIS-FreeRTOS (3), and first-party providers (216 across 69
bounded entries). The exact RTOS seam is the CMSIS-FreeRTOS v10.5.1 wrapper
`osKernelGetTickCount` (`0x004490CC`, 3 calls) over the admitted FreeRTOS
kernel; no direct kernel call occurs. First-party edges cover the closed
`terminal.c` core (`0x005E43D2`, 31 calls), `terminal_data.c`
(`0x005971xx`–`0x005976xx`), `terminal_timer.c` (`0x005E7EC4`–`0x005E7FC0`),
the query panel and session model clusters (`0x005EA2A8`–`0x005ED152`), the
closed `pb_service_terminal.c` (`0x005CEC72`–`0x005CF134`), audio manager
(`0x0054F380`, `0x0054F50E`), and list/fade anim helpers
(`0x0058966C`–`0x0058C426`).

This reuses EasyLogger `a596b264…`, LVGL `344c7c31…`, CMSIS-FreeRTOS
`d213f261…`, and FreeRTOS `def7d2df…`. The object embeds no third-party
implementation and adds no new version or private generating-commit
discriminator.

## Limitations

The seventy-six restored functions carry source-order and call-graph
evidence only; their original C names are unobservable. The single `blx`
dispatch is data-driven through a runtime-populated session struct and is
documented rather than constant-bound; its supplier tables are pinned by the
stored-pointer censuses named above. `terminal_timer.c`, the query panel
object, and the preceding session-model cluster remain open first-party
objects with their own closures pending. The object is not production-routed;
first-party terminal recreation and device display validation remain open
work.
