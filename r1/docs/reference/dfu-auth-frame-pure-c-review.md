# R1 DFU authorization C frame, 2026-11-10

`r1/src/application/runtime/native_dfu_ble_event.c` now uses a local volatile
word array and an ordinary C call to `authorize_kernel` for
`r1_native_dfu_ctrlpt_authorize`. It replaces the handwritten stack push,
allocation, call and pop. The selected Clang profile saves two registers and
allocates ten words, so the frame pointer passed to the kernel is entry SP-48,
the same address as the native four-register save plus eight-word allocation.
The resulting wrapper uses different prologue and epilogue instructions; its
complete object is not byte-identical to the previous one.

The existing paired stock/C DFU authorization replay was copied into the
ignored `build/r1-dfu-auth-frame-probe-20261110/` directory and run with
`AUTH_REPORT=build/r1-dfu-auth-frame-c-20261110/report.json`. It passed 5,002
core cases without the backend chain, 1,744 with the chain, and 1,168 plus
304 integrated control-dispatch cases. The fixture compares authorization
reply bytes, pointer aliases, status and busy retry behavior, backend event
effects and returns; service and shutdown behavior remain modeled. It excludes
private saved-register and incidental caller-clobbered state as documented in
the [earlier DFU SDK review](dfu-auth-sdk-c-review.md).

The 959-unit R1 source build has no failed units or duplicate strong symbols.
The strict bootloader link passes. The application still has 43 undefined
references and a 28,240-byte full flash load overflow. Physical BLE/SoftDevice
operation, board execution and stock bundle byte identity remain unverified.
