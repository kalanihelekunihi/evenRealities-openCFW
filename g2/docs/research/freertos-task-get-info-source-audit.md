# FreeRTOS `vTaskGetInfo` production source audit

Status: authenticated FreeRTOS-Kernel V10.5.1 source, production-routed in the
Apollo-main Apple Clang profile. No signing, flashing, debugger, or hardware
operation was performed.

## Result

The complete stock `vTaskGetInfo` body at `[0x00455728,0x004557A8)` is 128
bytes with SHA-256
`53d97f8c2e506f69df7908f9b3d2c644fd4f21b456f5961311f1ce34d975f626`.
Its instruction sequence matches the authenticated V10.5.1 implementation
under the recovered G2 configuration:

- `configUSE_TRACE_FACILITY=1`, `configUSE_MUTEXES=1`;
- `configGENERATE_RUN_TIME_STATS=0`, `INCLUDE_vTaskSuspend=1`;
- downward-growing stacks, four-byte `StackType_t`, and a 16-bit stack-depth
  result;
- 32-byte task names and the vendor-extended 112-byte TCB ABI; and
- the IAR one-byte `eTaskState` representation in the 36-byte `TaskStatus_t`.

The source adaptation is
`components/shared/freertos/runtime_freertos_task_get_info.c`. Apple Clang
21 emits one 120-byte text leaf at overlay offset 164792 / runtime
`0x007BC6DC`. Its unrelocated SHA-256 is
`853e2b1f7fd21913e9f51dea0edb8252a131712628a583d875a8b7e15f01d393`;
after four reviewed Thumb relocations the SHA-256 is
`d11bed3afc9fd39e0315d3efa1cbe5dac85d723e90009103b67bf39420d9995d`.

The relocations bind only to earlier source-owned entries:

| Leaf offset | Provider |
| ---: | --- |
| `+60` | `open_cfw_freertos_task_get_state` |
| `+76` | `open_cfw_freertos_task_suspend_all` |
| `+90` | `open_cfw_freertos_task_resume_all` |
| `+110` | `open_cfw_freertos_task_check_free_stack_space` |

The current-TCB word remains the recovered fixed global at `0x20074A20`.
Static assertions pin every accessed TCB field and the public status-record
offsets. Host tests cover null-handle current-task selection, supplied and
computed states, the suspended-versus-indefinitely-blocked distinction,
scheduler suspend/resume pairing, metadata copies, and optional stack scanning.

The full stock body is replaced by a guarded `B.W` and NOP fill. The resulting
Apple overlay/component/package identities are `164912/3688308/4466802` bytes
with SHA-256 values
`8c65ebb25586f80cc4eaec62fd9442c0dc28a37a897fec7349822d980cc767e0`,
`4dea653f6001fc9cf287253481ab412d9046a590bc70707fadce6afb01307b09`, and
`03292baa960e39beb368b32a0b93f3f68d13caf6db121a2bb6020363c366afa0`.

This promotion closes the ledger's remaining public FreeRTOS task/queue-private
row. Scheduler-start and Apollo STIMER/tickless work remain separate gaps; the
latter still requires authorized physical timing and power evidence.
