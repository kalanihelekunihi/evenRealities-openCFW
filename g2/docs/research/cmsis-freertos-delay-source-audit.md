# CMSIS-FreeRTOS delay source audit

Status date: 2026-08-10  
Target: official G2 `s200_v2.2.6.10`

## Result

`vTaskDelay` and `osDelay` are production source-owned as one closed unit.
The FreeRTOS implementation comes from Kernel V10.5.1 commit
`def7d2df2b0506d3d249334974f51e427c17a41c` under MIT; the wrapper comes from
CMSIS-FreeRTOS v10.5.1 commit
`d213f261b5be6bb29a7cce8b84071706b72f4d53` under Apache-2.0.

| Function | Stock span | Bytes | Stock SHA-256 |
|---|---:|---:|---|
| `vTaskDelay` | `[0x00454B4C,0x00454B88)` | 60 | `86f7d3b317ec02d559374d2bdb113698889a1291d8d4369f255d2c6874015738` |
| `osDelay` | `[0x00449376,0x00449398)` | 34 | `86584b9833b32e166acbeeea1a4c08671b20ac1fa10b15746d824c4b03311718` |

The task adapter preserves the zero-delay yield, suspended-scheduler
assertion, scheduler suspend/resume pair, finite delayed-list placement, and
yield suppression when resume already yielded. Every dependency is separately
source-owned. The CMSIS wrapper preserves ISR rejection and its zero-tick
no-call behavior.

Apple emits 70- and 30-byte leaves at overlay offsets `135292` and `135364`;
Linux emits the same sizes at `137168` and `137240`. At this tranche boundary,
the packages were `4437284` / `7f3c2c79461c4dec4d01b1ef358a8cfbc3fd98c59abd570700eba4ca3ce96043`
and `4439160` / `64229a7e9a1f1d4ab6d25fbd1555f247dad48b8d7dbf9b33320dad1d6b41a4a3`.
This was the 31st of 38 linked public CMSIS APIs; the later priority-set
closure supplies the current aggregate boundary. No image was signed or
flashed.
