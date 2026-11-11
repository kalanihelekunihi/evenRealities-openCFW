/* SPDX-License-Identifier: MIT
 * Reconstructed local wrapper 0x41f9d8: millisecond delay on top of
 * am_hal_delay_us. The other stock wrappers of this group are aliases of the
 * AmbiqSuite functions they reproduce: 0x41ac44 am_hal_sysctrl_fpu_enable and
 * 0x41ac5a am_hal_sysctrl_fpu_stacking_enable ({gen}/ambiqhal-apollo510-boot/
 * am_hal_sysctrl.c), and the raw microsecond delay am_hal_delay_us
 * ({gen}/ambiqhal-apollo510-boot/am_hal_utils.c).
 */
#include <stdint.h>

#include "local_providers.h"

extern void am_hal_delay_us(uint32_t ui32us);

void opencfw_boot_delay_scaled(uint32_t milliseconds)
{
    am_hal_delay_us(milliseconds * 1000u);
}

/* Stock entry names of the provider above. */
__typeof__(opencfw_boot_delay_scaled) opencfw_bl_delay __attribute__((alias("opencfw_boot_delay_scaled")));
__typeof__(opencfw_boot_delay_scaled) opencfw_provider_41f9d8 __attribute__((alias("opencfw_boot_delay_scaled")));
