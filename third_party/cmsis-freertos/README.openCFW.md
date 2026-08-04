# CMSIS-FreeRTOS v10.5.1 constructor compile-input closure

This directory contains unmodified files from two official Arm repositories:

- CMSIS-FreeRTOS tag `v10.5.1`, annotated tag object
  `34e6e4c403c17de35ec0acf29610e374dc938604`, commit
  `d213f261b5be6bb29a7cce8b84071706b72f4d53`, and tree
  `d3689a816acc77a3f0b7d35439d666ad8434b6ba`; and
- CMSIS_5 tag `5.9.0`, annotated tag object
  `61e36449f53c25ef7825c40f7dd93685736f457f`, commit
  `2b7495b8535bdcb306dac29b9ded4cfb679d7e5c`, and tree
  `b88e747b2a2309b81ea77831481a58393465cd7b`.

Both annotated tags are unsigned. `PROVENANCE.json` therefore pins the official
repository URLs, tag objects, peeled commits, trees, and every imported file by
source path, byte count, Git blob SHA-1, and SHA-256.

## Why CMSIS 5.9.0 is included

The authenticated CMSIS-FreeRTOS package descriptor
`CMSIS-FreeRTOS/ARM.CMSIS-FreeRTOS.pdsc` declares an exact dependency on
`ARM::CMSIS@5.9.0`. The public `cmsis_os2.h`, `os_tick.h`, and compiler headers
are copied from that exact official CMSIS_5 tag rather than inferred from a
newer checkout.

The bounded compiler path is GNU-compatible: `cmsis_compiler.h` selects
`cmsis_gcc.h` when `__GNUC__` is defined, including with the Clang-based
openCFW reconstruction toolchain. Other compiler backends are intentionally
outside this snapshot.

## Compile boundary

The translation unit is:

`CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c`

Its local include directories are:

- `CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Include`
- `CMSIS_5/CMSIS/RTOS2/Include`
- `CMSIS_5/CMSIS/Core/Include`

A compile also needs the separately authenticated
`../freertos-kernel/include` closure, an externally selected FreeRTOS
`portmacro.h`, a reviewed G2 `FreeRTOSConfig.h`, and the C implementation's
standard headers. Those device/project inputs are deliberately not invented
or copied into this pristine vendor snapshot.

The bounded path leaves `_RTE_` undefined. Defining `_RTE_` would add
target-specific `RTE_Components.h`, a CMSIS device header, and potentially
Event Recorder inputs; those are not part of this authenticated closure.

## Status

This is a source/header authentication milestone for the
`osMessageQueueNew`, `osMutexNew`, and `osSemaphoreNew` reconstruction work.
It is not wired into a builder or firmware manifest and is not evidence of
production readiness. G2 object attributes, recovered FreeRTOS configuration,
ABI/layout behavior, relocations, and fixed-address integration remain
separate review gates.

## Offline verification

Run:

```sh
python3 openCFW/third_party/cmsis-freertos/verify_snapshot.py
```

The verifier reads only this directory. It checks the exact subtree inventory,
provenance identities, file bytes and Git blob identities, the declared CMSIS
5.9.0 dependency, direct include closure, constructor markers, compiler-branch
selection, and retained license notices. It performs no network or hardware
operations and does not compile or link firmware.

## License

The wrapper source and CMSIS headers retain their Apache-2.0 notices. The full
CMSIS_5 Apache-2.0 license is retained as `CMSIS_5/LICENSE.txt`.
CMSIS-FreeRTOS's original `License/license.txt` is also retained byte-for-byte;
it records the MIT terms for the separately supplied FreeRTOS kernel.
