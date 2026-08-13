# FreeRTOS stack-overflow configuration correlation

## Result

The exact 72-byte function `0x00095BFC..<0x00095C44`, SHA-256
`bcfd3bdbdaad628a3ac9e550e4bd7b5a14f25d994357e84a5e250d2ebfddf8da`,
is the R1 application's `vApplicationStackOverflowHook` configuration callback.
Its only direct callsite is `0x000965E4` inside the exact Nordic SDK-bundled
FreeRTOS-Kernel 10.5.1 `vTaskSwitchContext` path.

The callback reports `Stack overflow in task: %s`, drains Nordic's logging
provider until empty, and then never returns. The two embedded diagnostic
forms at `0x00095C44` and `0x00095C70`, the complete body, and its caller are
verifier-pinned. The census is reproducible with:

```sh
python3 tools/evidence/summarize_r1_freertos_stack_overflow.py
```

## Recovered kernel configuration

The caller checks the first four stack words against `0xA5A5A5A5` before it
invokes the hook. This is the exact downward-growing-stack expansion selected
by `configCHECK_FOR_STACK_OVERFLOW > 1` in authenticated FreeRTOS-Kernel 10.5.1's
`stack_macros.h`. openR1 therefore sets `configCHECK_FOR_STACK_OVERFLOW` to 2.

FreeRTOS owns the sentinel fill, `vTaskSwitchContext`, stack macro, TCB layout,
and scheduling behavior. R1 owns only the callback's diagnostic and fail-stop
policy. The linked clean-room callback writes a bounded diagnostic through the
already admitted SDK-bundled SEGGER RTT provider and does not return. It does
not recreate Nordic's logging frontend or any FreeRTOS kernel body.

## Admission decision

- provider family: `r1_provider_configuration_glue`;
- disposition: `clean_room_configuration_only_use_pinned_provider`;
- local implementation: callback diagnostic/fail-stop behavior only;
- upstream implementation: the complete FreeRTOS check and scheduler path.

No FreeRTOS function body is recreated locally.
