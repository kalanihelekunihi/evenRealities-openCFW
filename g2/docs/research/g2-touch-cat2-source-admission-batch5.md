<!-- SPDX-License-Identifier: MIT -->
# G2 touch CAT2 source admission: batch 5

The final ten CAT2 candidates were audited individually against public
Apache-2.0 source at pinned `mtb-pdl-cat2` commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`.

Nine have exact authenticated provider bodies:

| Entry | Public symbol | Provider family |
|---:|---|---|
| `0x5CA0` | `Cy_MSCLP_Capture` | MSCLP |
| `0x5CD0` | `Cy_MSCLP_Configure` | MSCLP |
| `0x6044` | `SlaveHandleHsMode` | SCB I²C private helper |
| `0x60C4` | `SlaveHandleStop` | SCB I²C private helper |
| `0x6210` | `SlaveHandleAck` | SCB I²C private helper |
| `0x62B8` | `SlaveHandleAddress` | SCB I²C private helper |
| `0x6448` | `SlaveHandleDataReceive` | SCB I²C private helper |
| `0x64FC` | `SlaveHandleDataTransmit` | SCB I²C private helper |
| `0x70B0` | `Cy_SysPm_RegisterCallback` | SysPm |

The source admission pins whole provider-file hashes, function-banner lines,
shipped instruction hashes, canonical target register signatures, and SCB
helper call edges. The isolated adapter compiles for Cortex-M0+ and exposes
typed callbacks; host execution performs no MSCLP, SCB, or power MMIO.

`0x7038` is exactly a two-byte non-returning self-loop. The pinned public
`cy_syslib.h` changelog states that `Cy_SysLib_Halt` was removed, and the pinned
provider supplies no authentic implementation body. The entry is therefore not
source-admitted. It remains a typed external system-provider boundary whose
adapter returns a fail-closed error when no explicit provider is installed.

This batch reduces the CAT2 source gap from ten to one and the overall
semantic/source gap from 175 to 166. The one remaining CAT2 row is fully typed,
not behavior-opaque. Mixed CAPSENSE, EULA, application/startup, and DFU/system
boundaries remain unchanged.
