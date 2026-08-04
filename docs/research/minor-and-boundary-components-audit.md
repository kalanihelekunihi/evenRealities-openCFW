# Minor and boundary component classification audit

Status: research-only identification. No production overlay, manifest, release
pin, shared coverage document, or firmware artifact changed. Run addresses use
the confirmed load base `run = file_offset + 0x00437FE0`.

This audit classifies three components the inventory lists as small or
uncertain boundaries, so later work does not mistake Even-proprietary framework
code for a vendorable upstream import.

## FreeRTOS-Plus-CLI — stock, paired with FreeRTOS-Kernel V10.5.1

| Evidence | Run address / value |
|---|---|
| Canonical interpreter string `Command not recognised.  Enter 'help' to view a list of available commands.` | present (verbatim stock `FreeRTOS_CLIProcessCommand` output) |
| `help:` help-command label | present |
| Vendored path `kernel\FreeRTOS-Plus-CLI\prvCommand\prvCommand_filesystem.c` | `0x006DE434` |

The verbatim interpreter string identifies **unmodified FreeRTOS-Plus-CLI**.
The application layers its own command table (a `prvCommand_filesystem`
module) on top; the core `FreeRTOS_CLIProcessCommand` /
`FreeRTOS_CLIRegisterCommand` and the `CLI_Command_Definition_t`
`{pcCommand, pcHelpString, pxCommandInterpreter, cExpectedNumberOfParameters}`
descriptor are stock. Because Plus-CLI ships alongside the FreeRTOS kernel and
the image already pins FreeRTOS-Kernel V10.5.1, the matching Plus-CLI drop is
the natural vendor pin. Remaining focused check: read
`configCOMMAND_INT_MAX_OUTPUT_SIZE` (the output buffer length) and the maximum
parameter count from the CLI process function before vendoring; the descriptor
ABI itself is already fixed by the canonical struct.

## `third_party\ringBuffer\ringbuffer.c` — generic, unattributed

| Evidence | Run address |
|---|---|
| Vendored path `third_party\ringBuffer\ringbuffer.c` | `0x006FC92C` |

This is a single-file generic ring buffer with no author, license, or version
signature string anywhere in the image. It carries no discriminating evidence
to attribute it to a specific published library (e.g. `jnk0le/Ring-Buffer` or
`AndersKaloer/Ring-Buffer`), so it **remains an uncertain boundary** and should
be treated as a small clean-room re-creation from a behavioral contract rather
than assigned an upstream identity.

## `framework\fw_event_loop\fw_event_loop.c` — Even-proprietary, not a vendor target

| Evidence | Run address |
|---|---|
| Vendored path `framework\fw_event_loop\fw_event_loop.c` | `0x006F3C38` |
| `[evtloop][fw_evt_loop_push_delayed] ...` diagnostics | present |
| `[evtloop][fw_evt_loop_task] app treat event invalid status:%d` | present |
| `[evtloop] Warning: failed to Create fw_evt_loop_mutex_id` | present |

The `evtloop` label in the inventory's "uncertain or proprietary boundaries"
is Even's **own** `framework/fw_event_loop` — a thin RTOS event-loop dispatcher
(`fw_evt_loop_push`, `fw_evt_loop_push_delayed`, `fw_evt_loop_timer_callback`,
`fw_evt_loop_task`) built on the already-source-integrated FreeRTOS/CMSIS timer
and mutex primitives. It is not a third-party library and needs no external
attribution; when source is developed it is a clean-room re-creation from the
recovered behavioral contract, sitting above the source-owned RTOS layer.

This audit does not sign, flash, connect to, or mutate hardware.
