/* Native flash program mode transitions 0x47f3c6 and 0x47f418. */
#include <stdint.h>

extern uint8_t audio_ble_flash_mode; /* native RAM 0x20074f62 */
extern uint32_t audio_ble_flash_control(uint32_t, uint32_t, const uint32_t *); /* 0x480312 */

uint32_t audio_ble_flash_enter_program_mode(void) {
    if (audio_ble_flash_mode != 1u) return 0u;
    uint32_t command = *(volatile uint32_t *)0x40021018u | 0x80u;
    (void)audio_ble_flash_control(5u, 1u, &command);
    *(volatile uint32_t *)0x40021014u |= 0x20u;
    uint32_t i = 0u;
    while (i < 10000u &&
           ((*(volatile uint32_t *)0x40021018u & 0x80u) == 0u)) i++;
    return i == 10000u ? 4u : 0u;
}

uint32_t audio_ble_flash_leave_program_mode(void) {
    if (audio_ble_flash_mode != 1u) return 0u;
    *(volatile uint32_t *)0x40021014u &= ~0x20u;
    uint32_t i = 0u;
    while (i < 10000u &&
           ((*(volatile uint32_t *)0x40021018u & 0x80u) != 0u)) i++;
    if (i == 10000u) return 4u;
    uint32_t command = *(volatile uint32_t *)0x40021018u;
    (void)audio_ble_flash_control(5u, 0u, &command);
    return 0u;
}
