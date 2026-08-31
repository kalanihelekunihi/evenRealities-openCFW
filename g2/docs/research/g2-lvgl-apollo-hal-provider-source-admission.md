# G2 LVGL Apollo HAL provider source admission

Status date: 2026-08-30  
Scope: the five Apollo HAL imports in the maximal LVGL/Ambiq/Nema link  
Mode: authenticated source reuse, exact ABI adapter, hostile host forwarding
tests, and Cortex-M55 relocatable-link verification; no production routing,
MMIO execution, flashing, or hardware operation

## Result

The largest coherent source-implementable platform group in the 78-symbol
atomic residual is now closed by an isolated component-local provider:

- `am_hal_cachectrl_dcache_clean`;
- `am_hal_cachectrl_dcache_invalidate`;
- `am_hal_pwrctrl_periph_disable`;
- `am_hal_pwrctrl_periph_enable`; and
- `am_hal_pwrctrl_periph_enabled`.

`third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_apollo_hal_provider.c`
exports those exact AmbiqSuite names and forwards them to the already
source-qualified `open_cfw_*` implementations. The adapter statically pins the
Apollo510 cache-range structure to eight bytes, the peripheral enum to the
one-byte short-enum ABI, and `bool` to one byte. It does not duplicate power or
cache policy and does not silently substitute the non-G2 Apollo510-EVB port.

The atomic missing-provider ledger falls from 78 to 73 symbols. Its canonical
digest is
`c015abdd95ca5c7692245988b262e05cc10e9d60382e7164473195c4d236739e`.
No `am_hal_*` symbol remains unresolved. This is source and link admission,
not production-overlay or hardware admission.

## Source boundary

The provider builds ten pinned C inputs independently: the MIT adapter plus
the existing cache, peripheral descriptor, peripheral enable/disable/status,
GPU-mode, shared-domain-mask, delay, and IRQ implementations. The adapted HAL
algorithms have already been bounded against complete stock bodies and the
AmbiqSuite SDK 5.1.0 compatibility source. The selected public replay is
Ambiq commit `5efc0228528a8adce5eae0d226fac85d2551eb3b`; the SDK files identify
revision `release_sdk5p1p0-366b80e084`. Ambiq's BSD-3-Clause terms and the
MIT adapter terms are retained in the repository.

This evidence does not claim that the local adaptations are unmodified public
translation units or the unavailable historical private generating source.
The atomic auditor instead pins every selected local input by path, byte size,
SHA-256, and license identifier and inherits the stock-body, call-topology,
host-model, and source-ancestry evidence recorded for those inputs in the
Apollo core-overlay evidence. No shared core source is modified by this
provider.

## ABI and relocation closure

Each input is compiled independently with Clang for
`arm-none-eabi`, Cortex-M55, Thumb, hard float, short enums, freestanding GNU
C11, `-O2`, section splitting, and warnings as errors. `ld.lld -r` then retains
the five exact Ambiq exports and their reachable implementation closure.

The adapter object has exactly one Thumb call/jump relocation to each of:

- `open_cfw_cache_dcache_clean`;
- `open_cfw_cache_dcache_invalidate`;
- `open_cfw_pwrctrl_periph_disable`;
- `open_cfw_pwrctrl_periph_enable`; and
- `open_cfw_pwrctrl_periph_enabled`.

The final 11,320-byte object has SHA-256
`04504e7e026eb53a08a187e037269d0f42a2e818842fc5320710c2a5952a06b7`.
It has no ELF undefined symbol. The auditor pins its complete 15-symbol
external export set, not only the five required aliases. Any source, object,
export, import, relocation, size, or digest drift fails closed.

## Hostile-input boundary

`tests.test_runtime_lvgl_ambiq_apollo_hal_provider` builds the adapter natively
with short enums and controlled providers. It proves exact return propagation,
full one-byte peripheral values, cache address/size forwarding, canonical
`bool` conversion to zero or one, and pointer identity for valid and null cache
and enabled-state pointers. The adapter intentionally preserves the public
HAL contract; it does not dereference or invent validation for pointers owned
by the underlying implementation.

The existing implementation-specific tests remain responsible for cache
maintenance sequencing, null cache range semantics, disabled-cache behavior,
peripheral descriptor failures, low-byte enum behavior, shared-domain power
policy, GPU sequencing, timeout paths, and null enabled-state rejection.

## Fixed-address and physical boundary

ELF import closure is not equivalent to a standalone hardware implementation.
The selected source materializes MMIO and eleven authenticated fixed G2 calls:

| Address | Role |
|---|---|
| `0x00000041` | ITCM delay-cycle entry |
| `0x0047F90D` | stock peripheral-enabled entry |
| `0x004803C3` | stock GPU TON update entry |
| `0x0048032D` | stock temperature-coefficient postpone entry |
| `0x004C44BD` | stock clock request entry |
| `0x00480313` | stock SPOT update entry |
| `0x00480343` | stock temperature-coefficient pending entry |
| `0x00480827` | stock status-check entry |
| `0x004807FD` | stock status-change entry |
| `0x004C4531` | stock clock-release entry |
| `0x004C45A5` | stock clock-release-all entry |

The auditor requires each exact address to remain present in its reviewed
owning source. It does not execute the calls or MMIO and does not register the
provider in a production overlay. G2 cache coherency, power sequencing,
retention, interrupt safety, GPU command completion, suspend/resume, and
display output therefore remain blocked on authorized physical evidence and a
separate routing review.

## Reproduction

From `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_apollo_hal_provider
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

The next coherent group—the three configured FreeRTOS queue/semaphore
imports—is now closed in isolation by the separately audited component-local
provider. Neither provider is production-routed or runtime-qualified here.
