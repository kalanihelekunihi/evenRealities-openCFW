/* Static helpers of the Macronix MX25U25643G NOR driver (MSPI1), stock
 * D:\01_workspace\s200_ap510b_iar_git\driver\flash\drv_mx25u25643g.c.
 * Native 0x46f4a4..0x46f50c and 0x46f6e6..0x46f788 of object
 * 0x46f4a4..0x471163; the other bodies are in drivers/flash/mx25u25643g.
 *
 * 0x46f4a4/0x46f4c2 are the file-local CMSIS __NVIC_EnableIRQ and
 * __NVIC_SetPriority copies (NVIC ISER 0xe000e100, IPR 0xe000e400, SHPR
 * 0xe000ed18, 3 priority bits in the top of each byte => value << 4).
 * 0x46f4ea is the MSPI1 vector (vector-table slot 37 at 0x438094 holds
 * 0x46f4eb, IRQ 21 = MSPI1_IRQn). 0x46f6e6/0x46f6fa are the Ambiq timing-scan
 * helpers count_consecutive_ones / find_mid_point used by mspi_timing_check. */
#include <stdint.h>
#include <stdbool.h>

#define NVIC_ISER_BASE 0xe000e100u
#define NVIC_IPR_BASE 0xe000e400u
#define SCB_SHPR_BASE 0xe000ed18u

extern volatile uint32_t g2_norflash_controller_handle_20074544; /* RAM 0x20074544, MSPI1 HAL handle */

extern uint32_t am_hal_mspi_interrupt_status_get(void *handle, uint32_t *status,
                                                 bool enabled_only); /* 0x4c2392 */
extern uint32_t am_hal_mspi_interrupt_clear(void *handle, uint32_t mask); /* 0x4c23de */
extern uint32_t am_hal_mspi_interrupt_service(void *handle, uint32_t status); /* 0x4c240e */

void nvic_enable_irq_46f4a4(int16_t irq);
void nvic_set_priority_46f4c2(int16_t irq, uint32_t priority);
void am_mspi1_isr_46f4ea(void);
uint32_t timing_window_length_46f6e6(const uint32_t *mask);
uint32_t timing_window_center_46f6fa(const uint32_t *mask);

/* 0x46f4a4 */
void nvic_enable_irq_46f4a4(int16_t irq)
{
    if (irq >= 0) {
        ((volatile uint32_t *)NVIC_ISER_BASE)[(uint32_t)(int32_t)irq >> 5] =
            1u << ((uint32_t)irq & 0x1fu);
    }
}

/* 0x46f4c2 */
void nvic_set_priority_46f4c2(int16_t irq, uint32_t priority)
{
    if (irq >= 0) {
        ((volatile uint8_t *)NVIC_IPR_BASE)[irq] = (uint8_t)(priority << 4);
    } else {
        ((volatile uint8_t *)SCB_SHPR_BASE)[((uint32_t)(int32_t)irq & 0xfu) - 4u] =
            (uint8_t)(priority << 4);
    }
}

/* 0x46f4ea: am_mspi1_isr. */
void am_mspi1_isr_46f4ea(void)
{
    uint32_t status;
    void *handle = (void *)(uintptr_t)g2_norflash_controller_handle_20074544;

    (void)am_hal_mspi_interrupt_status_get(handle, &status, false);
    (void)am_hal_mspi_interrupt_clear((void *)(uintptr_t)g2_norflash_controller_handle_20074544,
                                      status);
    (void)am_hal_mspi_interrupt_service((void *)(uintptr_t)g2_norflash_controller_handle_20074544,
                                        status);
}

/* 0x46f6e6: count_consecutive_ones, the longest run of set bits. */
uint32_t timing_window_length_46f6e6(const uint32_t *mask)
{
    uint32_t count = 0u;
    uint32_t data = *mask;

    while (data != 0u) {
        data &= data << 1;
        count++;
    }
    return count;
}

/* 0x46f6fa: find_mid_point, centre of the longest passing window, nudged
 * towards the side of the scan the window touches. */
uint32_t timing_window_center_46f6fa(const uint32_t *mask)
{
    uint32_t pattern_len = 0u;
    uint32_t max_len = 0u;
    uint32_t pick_point = 0u;
    bool pattern_start = false;
    uint32_t val = *mask;
    uint8_t remainder = 0u;
    bool pick_point_flag = false;

    for (uint32_t i = 0u; i < 32u; i++) {
        if (((val >> i) & 1u) != 0u) {
            pattern_start = true;
            pattern_len++;
        } else if (pattern_start) {
            pattern_start = false;
            pick_point_flag = true;
        }
        if (i == 31u && pattern_start)
            pick_point_flag = true;
        if (pick_point_flag) {
            if (pattern_len > max_len) {
                max_len = pattern_len;
                pick_point = i - 1u - (pattern_len >> 1);
                remainder = (uint8_t)(pattern_len & 1u);
            }
            pattern_len = 0u;
            pick_point_flag = false;
        }
    }
    if (pick_point < 16u && (val & 0x00000002u) != 0u)
        pick_point -= remainder;
    else if (pick_point >= 16u && (val & 0x40000000u) != 0u)
        pick_point += 1u;
    return pick_point;
}
