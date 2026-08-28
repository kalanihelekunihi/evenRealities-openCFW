# G2 touch runtime and CAT2 source admission

This tranche admits isolated source routes for four exact runtime ABI
candidates and nine of the 54 CAT2 PDL provider candidates. It performs no
production routing or hardware operation.

## Admitted routes

The four runtime boundaries use new MIT project code:

| Stock entry | Candidate | Isolated route |
|---:|---|---|
| `0x76ac` | exit wrapper | optional fini hook followed by mandatory halt provider |
| `0x76e4` | `__libc_init_array` | ordered preinit/init array walker |
| `0x7740` | `_exit` halt | fail-closed mandatory halt provider |
| `0x7744` | runtime init stub | empty initialization boundary |

The exit adapter deliberately returns unavailable when no halt provider exists;
it does not pretend a host test can implement the target’s non-returning halt.

Nine CAT2 functions have strong matches to Infineon `mtb-pdl-cat2` commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`:

- `Cy_SysLib_DelayUs` at `0x7024`;
- `Cy_SysPm_ExecuteCallback`, `Cy_SysPm_CpuEnterSleep`, and
  `Cy_SysPm_CpuEnterDeepSleep` at `0x7144`, `0x7228`, and `0x728c`; and
- `Cy_SysTick_ServiceCallbacks`, `Cy_SysTick_Enable`,
  `Cy_SysTick_SetClockSource`, `Cy_SysTick_Init`, and
  `Cy_SysTick_SetCallback` at `0x72f4`, `0x7320`, `0x7338`, `0x7350`, and
  `0x73a8`.

The Apache-2.0 adapter implements host-testable DelayUs and SysTick behavior.
SysPm remains a typed provider route so the authoritative upstream function can
own callback lists, critical sections, and low-power entry. No MMIO or WFI is
performed by the adapter.

Both sources compile freestanding for Cortex-M0+ Thumb and have host tests for:

- runtime array ordering and null-entry handling;
- fail-closed exit routing;
- DelayUs cycle multiplication;
- SysTick callback ordering, reload, and enable state; and
- fail-closed SysPm provider routing.

## Gap reduction

| Category | Before | Admitted | Remaining |
|---|---:|---:|---:|
| Exact runtime | 4 | 4 | 0 |
| CAT2 PDL candidates | 54 | 9 | 45 |
| Application/startup | 99 | 0 | 99 |
| Mixed CAPSENSE/CAT2 | 55 | 0 | 55 |
| Em_EEPROM EULA | 10 | 0 | 10 |
| System/DFU handoff | 1 | 0 | 1 |
| **Semantic/source gap** | **223** | **13** | **210** |

Address proximity alone does not admit the other 45 CAT2 candidates. They need
individual public-symbol/ABI evidence. Mixed CAPSENSE/CAT2, EULA, application,
and system-handoff rows remain non-concrete.

## Licensing

- New runtime adapters are MIT.
- CAT2 adapters and upstream CAT2 implementations retain Apache-2.0.
- The CAT2 adapter explicitly excludes Infineon-EULA source.
- No CAPSENSE, Em_EEPROM, private application, or mixed-provider source is
  admitted by this tranche.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 g2/tools/analyze_g2_touch_source_admission.py --write-manifests --json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest g2.tests.test_runtime_touch_source_admission g2.tests.test_analyze_g2_touch_source_admission
```
