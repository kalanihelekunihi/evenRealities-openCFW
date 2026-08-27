# G2 bootloader EasyLogger output-lock-enable source closure

The complete authenticated `elog_output_lock_enabled` body `[0x00417B7C,0x00417BB8)` is replaced by maintained C. The 60-byte stock body has SHA-256 `61ab2f07f409287f6b8773559ad3223a72a9550cd9fc25dadfc7cb3a9ddc1c32` and one direct caller at `0x00417366`.

`runtime_easylogger_lock_enabled_417b7c.c` is an MIT adaptation of EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. It writes the recovered logger flag at offset `+0xF2`, returns without a port action while disabled, re-locks when the saved pre-disable state was unlocked and the pre-enable state was locked, re-unlocks for the inverse transition, and leaves matching saved states unchanged. The port calls retain the exact Thumb seams `0x0041A69B` and `0x0041A6A3`.

Both reviewed toolchains emit the same relocation-free 36-byte leaf with SHA-256 `9ea9783eda65110ea7b7df1bfe4fdfbff1bc670a9bbc91e929f694110ef3cf3f`. Apple places it at overlay offset 8,840 (`0x00436700`); Linux places it at offset 8,824. The host test exercises disable, re-lock, re-unlock, and both no-op state combinations; the target test compiles the source freestanding for Cortex-M55.

No hardware was accessed. Live mutex state reconciliation and scheduler concurrency remain blocked by unavailable authorized responsive G2 hardware.
