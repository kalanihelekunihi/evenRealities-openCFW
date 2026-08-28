<!-- SPDX-License-Identifier: MIT -->
# G2 touch CAT2 source admission: batch 4

This offline batch admits nineteen shipped touch-controller functions to exact
public Apache-2.0 APIs at pinned `mtb-pdl-cat2` commit
`35f1714623cfea682d5e285af80d50416b4c7bbc`.

Four compact GPIO bodies are exact inline helpers used by the already admitted
`Cy_GPIO_Pin_Init`: `Cy_GPIO_SetHSIOM`, `Cy_GPIO_Write`,
`Cy_GPIO_SetDrivemode`, and `Cy_GPIO_SetInterruptEdge`.

Fifteen clock bodies map to public EXTCLK/IMO/ILO, HFCLK, and PERI divider
APIs. The set includes `Cy_SysClk_IloStartMeasurement`,
`Cy_SysClk_IloStopMeasurement`, and `Cy_SysClk_IloCompensate`; the latter is
identified by its 100-to-2,000,000 microsecond range checks and ILO counter
compensation arithmetic. It also includes HF clock source/divider frequency
handling and the integer/fractional peripheral-divider configuration commands.

Admission is gated by the authenticated shipped instruction hashes, canonical
register-signature hashes, public function-banner line locations, pinned whole
provider-file hashes, caller topology, Apache notices, and a Cortex-M0+ adapter
build. Host tests use typed callbacks and perform no GPIO, SRSS, or PERI MMIO;
missing callbacks fail closed.

The CAT2 remainder drops from 29 to 10 and the overall semantic/source gap from
194 to 175. The remaining entries are `0x5CA0`, `0x5CD0`, `0x6044`, `0x60C4`,
`0x6210`, `0x62B8`, `0x6448`, `0x64FC`, `0x7038`, and `0x70B0`. They remain
unadmitted pending separate SCB/device/system evidence. Mixed CAPSENSE, EULA,
application/startup, and DFU/system batches are unchanged.
