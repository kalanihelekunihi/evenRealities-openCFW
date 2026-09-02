# G2 bootloader command-queue adapter source closure

The three adjacent functions at `0x0042C3E2..0x0042C45A` are now source-owned MIT command-queue adapters. They initialize an embedded queue descriptor, publish the active flag only after successful initialization, establish the hardware queue link on first enable, and forward enable/disable requests to the already source-owned command-queue services.

The Arm implementation uses reviewable Thumb-2 mnemonics and three explicit `R_ARM_THM_CALL` provider relocations to `0x00427794`, `0x00427878`, and `0x004278C8`. Apple clang 21 and Homebrew clang 22 reproduce the authenticated 62-, 46-, and 12-byte bodies exactly. Portable host tests cover capacity conversion, success/failure publication, idempotent link setup, and provider result propagation. Live command-queue validation is blocked by unavailable physical evidence.
