# G2 CMSIS-FreeRTOS thread-yield source candidate

Status: source-integrated in the Apollo-main production overlay  
Target: official G2 `s200_v2.2.6.10`

`osThreadYield` is a 26-byte stock entry at
`[0x004491E4,0x004491FE)`, SHA-256
`b8041c6d93a504e7b04c942da7e83b370bf58ca1d567b2d938587ba8ecf1ffa7`,
with one external caller. Its only calls are the already source-owned
`IRQ_Context` and FreeRTOS `vPortYield` providers.

The bounded Apache-2.0 candidate
`components/apollo_main/core_overlay/runtime_cmsis_thread_yield.c` is 1,748
bytes, SHA-256
`c03ff1c35cd5ace0c26d927594960674b6e8a3c0fd1a8fb79f02d3d49c2552a5`.
Apple Clang emits 24 bytes, SHA-256
`603a20d58a9508fe505535ce6e7ab0084dc57f318eff1cfd9a201587926d7b7b`,
with exactly two Thumb calls at `+2` and `+16`. Host tests prove that task
context yields once and returns `osOK`, while ISR context never yields and
returns `osErrorISR`.

The complete stock span is now redirected to the linked source leaf. Apple
places it at offset 131,628 (`0x007B4550`) with linked SHA-256
`06afe2fbd2f46c349f1696fd235e58db5c2aaca8c593b774ca825a7899316bd6`;
Linux places it at offset 133,496 with linked SHA-256
`1e01b52f42aff4bccd6bea11cf7515e08ad88eefe7de1fefefd579e0d33c9e69`.
Run `make -C openCFW cmsis-freertos-thread-yield-candidate` for the focused
host/target and production-registration proof.
