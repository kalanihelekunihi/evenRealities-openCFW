/* SPDX-License-Identifier: MIT
 * Locked bootloader 41fe28/41fe48/41fe62. These are source semantics;
 * synthetic HAL execution is not evidence of physical peripheral state.
 */
#include <stdint.h>
#include "../thread_creation/resource_creators.h"
extern uint32_t opencfw_hal_power_control(uint32_t, uint32_t, uint32_t);
extern void opencfw_provider_4176ce(uint32_t, const char *, const char *,
                                  const char *, uint32_t, const char *, ...);
#define POWERED (*(volatile uint8_t *)(uintptr_t)0x200271c6u)
#define HANDLE (*(volatile uint32_t *)(uintptr_t)0x200270dcu)
#define MUTEX (*(volatile uint32_t *)(uintptr_t)0x200270e0u)
/* Authenticated 16-byte attributes at 433cf8. The name address is data,
 * not an executable provider; the static CB is 80 bytes at 20026c60. */
static const uint32_t mutex_attributes[4] = {
    0x00433f2cu, 0u, 0x20026c60u, 80u
};
void opencfw_provider_41fe28(void) {
    if (POWERED != 1u) {
        (void)opencfw_hal_power_control(HANDLE, 2u, 1u);
        POWERED = 1u; /* Stock ignores HAL status; retain that behavior. */
    }
}
void opencfw_provider_41fe48(void) {
    (void)opencfw_hal_power_control(HANDLE, 0u, 1u);
    POWERED = 0u;
}
void opencfw_provider_41fe62(void) {
    if (MUTEX == 0u) {
        MUTEX = opencfw_provider_416610(mutex_attributes);
        if (MUTEX == 0u)
            opencfw_provider_4176ce(1u, "drv.norflash",
                "D:\\01_workspace\\s200_ap510b_iar_git\\driver\\flash\\drv_mx25u25643g.c",
                "mspi_flash_mutex_init", 0xbau,
                "failed to Create mspi_flash_mutex_id");
    }
}
