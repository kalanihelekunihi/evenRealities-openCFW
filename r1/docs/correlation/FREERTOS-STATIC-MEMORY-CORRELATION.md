# FreeRTOS static idle/timer memory correlation

## Result

Two exact functions / 36 executable bytes are the R1 application callbacks
required by `configSUPPORT_STATIC_ALLOCATION`:

| Entry / half-open extent | Caller | Recovered callback | Returned layout |
|---|---|---|---|
| `0x00095BB8..<0x00095BCA` | `vTaskStartScheduler` at `0x000964D8` | `vApplicationGetIdleTaskMemory` | control block `0x2002B4D0`, stack `0x2002B540`, 256 words |
| `0x00095BD0..<0x00095BE2` | `xTimerCreateTimerTask` at `0x00098CC2` | `vApplicationGetTimerTaskMemory` | control block `0x2002B940`, stack `0x2002B9B0`, 256 words |

Both 18-byte bodies have SHA-256
`2493b37197606152e480a50e74a2c99cfbfc851026f1545cb4ee3001568d1123`.
The pointer literals at `0x00095BCC` and `0x00095BE4`, direct caller sets, and
complete bodies are verifier-pinned. The static census is reproducible with:

```sh
python3 tools/evidence/summarize_r1_freertos_static_memory.py
```

## Provider/configuration split

Authenticated upstream FreeRTOS-Kernel 10.5.1 owns `vTaskStartScheduler`,
`xTimerCreateTimerTask`, task control structures, scheduler behavior, and the
callback contract. The recovered R1 application owns only the two fixed memory
allocations and their configuration callbacks. Accordingly:

- provider family: `r1_provider_configuration_glue`;
- disposition: `clean_room_configuration_only_use_pinned_provider`;
- local implementation: the two callback bindings and storage declarations;
- upstream implementation: all scheduler, timer, task, and list machinery.

No FreeRTOS function body is recreated locally.

## Exact layout

Each allocation is 1,136 bytes:

- 112 bytes for `StaticTask_t`;
- 1,024 bytes for 256 four-byte `StackType_t` words.

The timer allocation starts exactly `0x470` bytes after the idle allocation.
The recovered callbacks both return `0x100` words. openR1 therefore sets both
`configMINIMAL_STACK_SIZE` and `configTIMER_TASK_STACK_DEPTH` to 256 and uses
the upstream types in `openr1_scheduler.c`. A former 128-word timer-stack
setting was corrected because it did not match the stock R1 callback.

This is R1 configuration data and provider binding only; it does not copy an
SDK example implementation or reconstruct the FreeRTOS provider.

The corrected Nordic SDK image remains reproducible. Its HEX SHA-256 is
`48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf` and its
85,020-byte BIN SHA-256 is
`421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
