# CMSIS-FreeRTOS synchronization operations source audit

Status: production-integrated; Apple/Linux fail-closed replay verified  
Target: official G2 `s200_v2.2.6.10` Apollo-main application  
Scope: `osMutexAcquire`, `osMutexRelease`, and `osSemaphoreRelease`

## Result

Three high-fanout CMSIS-FreeRTOS synchronization wrappers now have one bounded
Apache-2.0 production source adapter:

| Wrapper | Stock span | Bytes | SHA-256 | External callers |
|---|---|---:|---|---:|
| `osMutexAcquire` | `[0x004497B6,0x0044981C)` | 102 | `86928d597f8f7b7f8f4519b40983a9384dfb72830fd2cec49809678bb1ff88a7` | 134 |
| `osMutexRelease` | `[0x0044981C,0x0044986E)` | 82 | `290de52cf203c2aaf8c554a686c675212c79382a696e46e0b70030363714eb71` | 153 |
| `osSemaphoreRelease` | `[0x004499B8,0x00449A0E)` | 86 | `5ff08a165bcf058ae1696528b092d64cbe7f6464b949763bc429597ad77b9d65` | 5 |

Together they cover 270 authenticated stock bytes and 292 external direct call
sites. The two mutex functions alone close 287 call sites, the largest
dependency-closed CMSIS admission opportunity presently available.

The selected oracle is Arm CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53`; its exact `cmsis_os2.c` blob was
first introduced by `13acfbef7be85119fc6bc56832c455d4547d92c7`. This is the
maintained source baseline, not proof of Even's unique historical checkout.

## Dependency closure

Authenticated stock disassembly contains only these fixed calls:

| Wrapper | Stock callee | OpenCFW provider |
|---|---|---|
| acquire | private `IRQ_Context` | `open_cfw_cmsis_irq_context` |
| acquire | `xQueueTakeMutexRecursive` | `open_cfw_freertos_queue_take_mutex_recursive` |
| acquire | `xQueueSemaphoreTake` | `open_cfw_freertos_queue_semaphore_take_upstream_candidate` |
| release | private `IRQ_Context` | `open_cfw_cmsis_irq_context` |
| release | `xQueueGiveMutexRecursive` | `open_cfw_freertos_queue_give_mutex_recursive` |
| release | `xQueueGenericSend` through `xSemaphoreGive` | `open_cfw_freertos_queue_generic_send` |
| semaphore release | private `IRQ_Context` | `open_cfw_cmsis_irq_context` |
| semaphore release | `xQueueGiveFromISR` | `open_cfw_freertos_queue_give_from_isr` |
| semaphore release | `xQueueGenericSend` through `xSemaphoreGive` | `open_cfw_freertos_queue_generic_send` |

Every listed provider is already a production source leaf pinned to the
authenticated CMSIS-FreeRTOS/FreeRTOS V10.5.1 lineage. The only non-call edge
is the standard Cortex-M PendSV request: successful ISR release writes
`0x10000000` to ICSR at `0xE000ED04` when the provider sets the yield flag.

This corrects the earlier priority note that treated mutex acquire/release as
blocked on a stock semaphore-take provider. The promoted
`open_cfw_freertos_queue_semaphore_take_upstream_candidate` leaf already
closes that edge atomically, despite retaining its historical candidate name.

## Recovered behavior

- Mutex handles use bit zero as the recursive tag; providers receive the
  untagged pointer.
- Mutex operations reject ISR context with `osErrorISR` (`-6`) and reject an
  untagged null handle with `osErrorParameter` (`-4`).
- Failed acquire maps a nonzero timeout to `osErrorTimeout` (`-2`) and zero
  timeout to `osErrorResource` (`-3`).
- Failed release maps to `osErrorResource`.
- Semaphore release accepts ISR context. It calls the ISR provider with an
  initially clear yield flag, requests PendSV only after a successful give
  that sets the flag, and maps a failed give to `osErrorResource`.
- Task-context semaphore release uses the same zero-timeout generic-send
  operation as upstream `xSemaphoreGive`.

The host fixture exercises validation, recursive/ordinary routing, every
success/failure mapping, timeout propagation, tag stripping, and the three ISR
yield outcomes. The target test independently pins each section and its exact
relocation contract under the reviewed Apple clang profile:

| Candidate section | Bytes | Unrelocated SHA-256 | Relocations |
|---|---:|---|---:|
| `open_cfw_cmsis_mutex_acquire` | 72 | `7c6c82e72e3edd4f081b91722d4bdbf1a8972867e25a58f23360fc4e0aa9b635` | 3 |
| `open_cfw_cmsis_mutex_release` | 64 | `495bd59cc9bd9361d84e1753467c90a81b09207976442fe1b7838e0bb2de9fe4` | 3 |
| `open_cfw_cmsis_semaphore_release` | 84 | `993c1b45a01e4c08abd7e0bd5ca4b9b6103dd373e18adb24130a743f51ce5115` | 3 |

## Production integration

All three leaves are registered atomically in `overlay.json`, each complete
stock entry has one authenticated `B.W` replacement, and the manifest records
the two-byte alignment plus three source regions. The final pins are:

| Profile | Overlay | Component/provider | Package |
|---|---|---|---|
| Apple clang 21 | `131980` / `262ddcb9b7a5e1c256465f14e07ce4a203f526b8fda19a89354803c0dce8ac92` | `3655376` / `1c599dd5c596052f3e2b751f1ffdef772eab48522aec14190779ef4fb9cfa2c2` | `4433870` / `8fe983ec88196b3ff3516a2f85fd15c3a728373c333a4965cfc38e41db47c8db` |
| Linux clang 22.1.8 | `133848` / `af94df32739f393884cbef722676bddd1413c0137661ae4b4a3d88cff0758bd3` | `3657244` / `8155d876e0ea2607c5283b7822068df995ed09fcb1c9e398163cd826a19ce9e2` | `4435738` / `10eb090b6bff4ce4bdb388b3492418a83549ba9b51742530899ccf11ba6860b0` |

Ordinary component and package builds reproduced all six aggregate artifacts
after the one-time profile records. The package delta is exactly 222 bytes:
220 source bytes plus two generated alignment bytes. It replaces 270 stock
bytes, so source ownership rises without expanding the opaque package count.
No signing, flashing, reset, boot, or hardware action was performed.

## Reproduction

```sh
make -C openCFW cmsis-freertos-sync-ops
```
