/* SPDX-License-Identifier: MIT. Independent locked-f89a4c46 reconstruction.
 * Numeric operations/registers preserve stock; no physical power guarantee.
 * Only the board external-mode cell remains: 0x41c7de, 0x41c86c, 0x41ca2c and the
 * SPOT simobuck wrappers 0x41cd76..0x41cda2 are upstream SDK 5.0.0 code. */
#include "startup_power_config.h"
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define NI __attribute__((noinline))
NI void opencfw_boot_startup_external_mode(uint32_t callback){W(0x200270ccu)=callback;}
