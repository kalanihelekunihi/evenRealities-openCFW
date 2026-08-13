# G2 terminal session list UI dependency boundary

The two retained-path anchors / 480 bytes expand to ten functions / 1,966
body bytes for `app\gui\terminal\terminal_session_list_ui.c`. The complete
physical object is `[0x005ED1EC,0x005EDA64)`, 2,168 bytes. Ghidra discovered
two functions; eight source-order routines were restored, completing the
session list table callbacks, panel transitions, and list refresh logic.

## Extent and boundaries

The object opens at `0x005ED1EC`, where the preceding unanchored
terminal-session cluster's last Ghidra function (`0x005ED1D6`–`0x005ED1EC`)
ends. Two fourteen-byte leading helpers (`0x005ED1EC`, `0x005ED1FA`) are
called only from inside the anchored session-list body (BL sites
`0x005ED544`, `0x005ED7AA`, `0x005ED2AE`), tying them to this object. The
object closes with a 168-byte trailing literal pool holding the path-pointer
cell `0x005ED9D8`. The following function `0x005EDA64` logs through the
`tlsf_init.c` path cell `0x005EDAD0` (literal reference `0x005EDA96`) and is
excluded as the third-party TLSF initializer. Boundary slices of 16 bytes on
both sides are hash-pinned.

## Function inventory and noncode

All ten functions are fully flow-covered with no embedded data. Four
inter-function/trailing literal pools (6 + 20 + 8 + 168 = 202 noncode bytes)
complete the physical object. Two functions are path-anchored (`0x005ED318`,
`0x005ED492`); all fourteen path-pointer literal references land inside the
recovered body.

## Ingress closure

The object is table-driven: twenty-five stored function entry pointers bind
every function except the two leading helpers. The cells form a regular
session descriptor table (`0x0065064C`–`0x00651414` with 0x140-byte strides
for the two create/configure entries, plus eight contiguous slots
`0x006512DC`–`0x006512FC`). Only three direct BL entry sites exist, all
internal to the body; there is no external direct BL ingress, no
strict-interior ingress, and no stored interior word.

## Provider boundary

All 131 external direct calls terminate at admitted providers: EasyLogger
(70), LVGL (5: `0x0043DED4`, `0x0043DFA4` object deletion/tree seams), and
first-party providers (56 across 27 bounded entries): the closed `terminal.c`
core (`0x005E43D2`), `terminal_data.c` helpers (`0x005973xx`), the closed
`pb_service_terminal.c` (`0x005CEE8C`, `0x005CEF14`, `0x005CEF8C`),
`terminal_ui.c` helpers (`0x005E5442`, `0x005E5484`, `0x005E57C6`), the query
panel object (`0x005EAE2C`, `0x005EBBC6`), and the immediately preceding
unanchored terminal-session cluster (`0x005EC268`–`0x005ED1D6`, eleven
entries). There are no CMSIS-FreeRTOS or FreeRTOS kernel edges and therefore
no RTOS seams in this object. The object embeds no third-party implementation
and adds no new version or private generating-commit discriminator.

## Limitations

The eight restored functions carry source-order and call-graph evidence
only; their original C names are unobservable. The preceding session-model
cluster and the query panel object remain open first-party objects with
their own closures pending. The object is not production-routed; first-party
terminal recreation and device display validation remain open work.
