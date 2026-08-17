# Task-topology startup correlation

## Decision

The explicit analysis seed at `0x00046B20` is an independent R1 startup
dispatcher. Its executable body is `0x00046B20..<0x00046B84` (100 bytes,
SHA-256 `32c34c30488b792c3e6af4b4d411adb9fba635857e81fcf2ee0354304b455f82`).
The complete code-and-literal envelope is `0x00046B20..<0x00046BAC` (140
bytes, SHA-256
`f6c8b8a76aa9208b6a16d0437a6a01f27fdfed719a160d196af39b2a33403be4`).
Its sole direct caller is the product startup path at `0x00045DA0`.

`r1_task_topology_startup_plan_build` represents the recovered order with
logical synchronization-group IDs. It contains no stock RAM address, task
handle, function pointer, or live task-creation operation.

## Recovered order

The dispatcher initializes the firmware event loop at `0x00065740`, then the
watchdog registry at `0x0005DAB4`. It invokes nine scatter-loaded task creators.
The task state blocks prove the same group mapping already pinned by the
suspend/boundary planner:

| Startup position | Normal group | Factory-marker `0x55` group |
| ---: | ---: | ---: |
| 1 | 0 | 0 |
| 2 | 1 | 1 |
| 3 | 2 | 2 |
| 4 | 3 | 3 |
| 5 | 10 | 10 |
| 6 | 4 | 4 |
| 7 | 7 | 7 |
| 8 | 5 | 6 |
| 9 | 9 | 9 |

After the first creator it sets the current thread priority to raw CMSIS value
`8`. After the remaining creators it tail-calls the same provider with final
priority `0x35`. Only position eight is configuration-dependent: state block
`0x20006608` (group 5) is replaced by `0x200066B0` (group 6) when the recovered
configuration byte is exactly `0x55`.

## Boundary

The source plan emits two preinitializer intents, the nine logical group IDs,
and both priorities. CMSIS-FreeRTOS and the authenticated FreeRTOS kernel own
thread creation and priority changes. The individually reconstructed task
startup functions own queue sizes, records, flags, watchdog periods, and
worker behavior. Firmware-event-loop execution and watchdog storage retain
their existing provider boundaries.

No caller can obtain or invoke the nine recovered creator pointers through
this API, and no scatter-loaded state address is compiled into the clean
planner. Host tests cover normal and exact-marker factory order plus all fixed
priorities and initializer intents.

## Verification

```sh
python3 tools/evidence/summarize_r1_task_topology_startup.py
```

The evidence script pins the application hash, both body hashes, sole caller,
all ten state-block literals, nine indirect calls, both preinitializers, the
configuration read, and both CMSIS priority callsites.
