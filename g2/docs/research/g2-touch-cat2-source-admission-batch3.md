<!-- SPDX-License-Identifier: MIT -->
# G2 touch CAT2 source admission: batch 3

This software-only tranche admits seven shipped touch-controller entries to
the public Apache-2.0 SCB common provider at pinned `mtb-pdl-cat2` commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`.

The six out-of-line functions occur in the same public source order and retain
the expected RX/TX FIFO register topology:

| Entry | Exact public symbol |
|---:|---|
| `0x5F18` | `Cy_SCB_ReadArrayNoCheck` |
| `0x5F50` | `Cy_SCB_ReadArray` |
| `0x5F6E` | `Cy_SCB_WriteArrayNoCheck` |
| `0x5FA6` | `Cy_SCB_WriteArray` |
| `0x5FD6` | `Cy_SCB_WriteDefaultArrayNoCheck` |
| `0x5FE6` | `Cy_SCB_WriteDefaultArray` |

`0x6016` is the public inline `Cy_SCB_SetRxFifoLevel`: its shipped body has
the FIFO-size assertion and RX FIFO trigger-level clear/set register pattern.
The analyzer pins the upstream source/header identities, shipped instruction
and canonical target-signature hashes, direct call edges, provider license,
and Cortex-M0+ adapter build.

The isolated adapter never performs host MMIO. Missing SCB providers return a
fail-closed result. The larger SCB I2C functions are not admitted here, nor are
mixed CAPSENSE, EULA, application/startup, or system rows. This batch reduces
the CAT2 candidate gap from 36 to 29 and the total semantic/source gap from 201
to 194 without making a hardware-readiness claim.
