# Storage task policy correlation

## Outcome

The Ghidra-omitted group-0 task at `0x00046954..<0x00046A2C` is now an exact manual
provenance supplement and an independently compiled pure plan. Its 216-byte body has SHA-256
`61783b8da754a2b95093818781cc1328f25b6143d9dcd983b285bb119f979e33`.
The creator literal at `0x00046A6C` contains odd Thumb pointer `0x00046955`.

This is the task that literally registers `"storage"`. It creates ten 16-byte records, joins
sync group 0, initializes its backend, schedules callback `0x0007CA71` after 3,072 ticks, signals
startup, and registers a 10,000-tick watchdog. The callback's pinned prefix emits internal event
`0x2005`. Successful low-24-bit waits use bit 22 to drain the queue non-blockingly and bit 23 to
signal suspension and enter the recovered indefinite wait. Provider-error flags skip dispatch.

The analysis also corrects the older label on `0x000926DC..<0x000927BA`. That distinct task has a
50-by-16-byte queue, sync group 7, ten health/database startup actions, and the literal registry
name `"service"`. It is represented by `r1_service_task_plan_startup` and
`r1_service_task_plan_flags`; the group-0 body maps to `r1_storage_task_plan_startup` and
`r1_storage_task_plan_flags`.

`python3 tools/evidence/summarize_r1_storage_task_policy.py` validates the body, creator and delayed
callback pointers, registry string, exact call topology, event prefix, and the corrected service
distinction against the rebuilt application image.

## Boundary

Both APIs are pure plans. They do not create CMSIS queues, call the private event dispatcher,
start a watchdog, signal a thread, wait forever, or execute storage/database work. Those effects
remain explicit bindings owned by the source scheduler and storage providers.
