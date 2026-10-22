/* SPDX-License-Identifier: MIT
 * CASE 0x0800a358 frame parser resynchronization.
 */
#include <stdint.h>
/* Stock 0x0800A358 (case_validate_magic_state) */
void case_boot_sensor_finish_reset(void)
{
    volatile uint8_t *const state=(volatile uint8_t *)(uintptr_t)0x20000108u;
    uint16_t length=*(volatile uint16_t *)(uintptr_t)0x2000010au;
    if(length>1u&&state[1]=='Z'){
        *(volatile uint8_t *)(uintptr_t)0x20000974u='Z';
        *(volatile uint16_t *)(uintptr_t)0x2000010au=1u;
    }else *(volatile uint16_t *)(uintptr_t)0x2000010au=0u;
}
