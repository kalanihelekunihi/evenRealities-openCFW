# 212...222-byte frontier correlation

The seven largest unresolved application functions after the 224...230-byte closure are now
source-routed from complete executable extents, immutable SHA-256 values, direct-call scans,
function-pointer references, strings, adjacent provider closures, and the recovered security audit.

| Recovered function | Executable bytes | Inventory bytes | Disposition |
| --- | ---: | ---: | --- |
| `0x00072FB8..<0x00073096` | 222 | 222 | Goodix GH3X2X signal-processing provider |
| `0x0008A45C..<0x0008A53A` | 222 | 222 | blocked unattributed sensor-stream framework |
| `0x0008F780..<0x0008F85C` | 220 | 220 | R1 stored-sleep ACK policy |
| `0x0008EF28..<0x0008F008` | 224 | 218 | R1 CmBacktrace/FreeRTOS diagnostic adapter |
| `0x0003E7A8..<0x0003E880` | 216 | 216 | R1 serialized Nordic BAE8 HVX adapter |
| `0x000628F6..<0x000629D2` | 220 | 214 | R1 system-control command `0x37` policy |
| `0x00063D50..<0x00063E2A` | 218 | 212 | R1 Nordic FDS-event adapter |

The tier contains 1,542 executable bytes versus 1,524 bytes reported by the Ghidra decimal-size
column. The three six-byte corrections follow the inclusive inventory ends and executable
disassembly through their actual return/tail boundaries.

## Provider boundaries

`0x00072FB8` is called only at `0x0007675A` inside the already gated Goodix processing pipeline.
It expands sign-mask decisions across contiguous positive or negative float runs and writes a
provider constant into the output. The adjacent threshold/mask builder at `0x0007309C` is also
Goodix-owned. This body is SHA-pinned as a provider boundary and is not reimplemented locally.

`0x0008A45C` is called by the sensor-stream scheduler at `0x00092344` and `0x000925D8`. It guards
against re-entry, traverses the framework's private linked list, dispatches due timer records,
computes the next minimum delay, and updates a 500-tick utilization statistic. The neighboring
timer dispatcher at `0x0008A1E0` is already blocked under the same unattributed framework. No
source, version, or license has been identified, so OpenR1 binds product code directly to admitted
providers and does not recreate this scheduler.

## Bounded R1 seams

The stored-sleep callback at `0x0008F780` is installed by Thumb pointer `0x0008F781` at
`0x0008DC08`. A null context only logs. Otherwise the callback publishes internal event `0x2001`
with the private 12-byte record-header/start/end context and frees the context after the attempt.
The policy neither exposes absolute flash addresses to the phone nor writes the synchronization
marker directly.

`0x0008EF28` is called only from the admitted CmBacktrace fault adapter. It uses authenticated
FreeRTOS `uxTaskGetSystemState`, maps task states to fixed names, asks the existing R1 saved-SP
adapter for each task's stack address, and renders stack-size/high-water data. This is an R1
diagnostic adapter; FreeRTOS task enumeration and CmBacktrace remain upstream providers.

`0x0003E7A8` selects one of the two BAE8 transmit semaphores, calls the already bounded HVX send,
normalizes accepted Nordic/application error values, releases the semaphore, and retries once
after 1,000 ticks only for status `0x13`. OpenR1 may own that serialization/retry decision while
CMSIS semaphores and Nordic S140 HVX remain provider code.

System-control command `0x37` at `0x000628F6` implements subcommands `0...5`, `13`, and
`0xFD...0xFF`. It shapes replies, samples a bounded configuration byte, performs fixed 200-tick
delays, and requests reset/tag actions. A clean-room implementation must expose reset and retained
tag writes as actions; it must not reset a device while parsing a packet.

The FDS callback at `0x00063D50`, registered through pointer `0x00063D51` at `0x0007E8B0`, maps
Nordic FDS event IDs `1...5` into R1 persistence events and retry bookkeeping. FDS owns record
validation and flash operations; the local seam may only translate validated event metadata and
request the next queued operation.

The clean-room implementation keeps product policy separate from provider execution.
`r1_sleep_sync_plan_acknowledgement` models event `0x2001`, the 12-byte private payload, publish
failure, and unconditional context release; `r1_system_control_command_37_plan` models reply
lengths, configuration-byte transitions, fixed 200-tick delays, retained-tag requests, and reset
actions. Neither function allocates, publishes, delays, persists, or resets.

The remaining seams use authenticated public provider APIs. `r1_bae8_plan_hvx_result` owns only
credit release and the one-retry-at-1,000-ticks decision; the existing CMSIS semaphore scheduler
consumes that plan and `openr1_bae8_transmit` continues to call Nordic S140 `sd_ble_gatts_hvx`.
`r1_fds_plan_event` translates already-validated FDS IDs and metadata into product event kinds,
while `openr1_storage_plan_fds_event` reads only the public `fds_evt_t` fields. It does not validate,
open, write, delete, or garbage-collect records. `openr1_cmbacktrace_log_task_snapshot` uses
FreeRTOS `uxTaskGetSystemState`; stack sizes come from OpenR1's own static task registry rather than
private TCB fields, and the existing CmBacktrace fault provider remains the unwinder.

The retained policy/adapter symbols are `r1_system_control_command_37_plan` at `0x0003642C`,
`r1_sleep_sync_plan_acknowledgement` at `0x00036842`, `r1_fds_plan_event` at `0x0003686C`,
`r1_bae8_plan_hvx_result` at `0x00038AE2`, `openr1_cmbacktrace_log_task_snapshot` at
`0x00039910`, and `openr1_storage_plan_fds_event` at `0x0003AFA8`. The linked image contains
94,804 bytes of text, 236 bytes of data, and 132,544 bytes of BSS. Its 95,040-byte BIN has SHA-256
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`; the standalone HEX has
SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_212_222.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

Code signing, deployment authorization, secrets, provider substitution, security-enforcement
bypasses, live device programming, and raw captured health data remain outside this closure.
