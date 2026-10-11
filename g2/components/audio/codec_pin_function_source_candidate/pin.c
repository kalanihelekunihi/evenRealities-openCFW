#include <stdint.h>

/* Stock 0x00480f0c..0x00480f89. These are capability masks from
 * authenticated read-only tables 0x768ba8 and 0x768bc4. */
static const uint32_t pin_function_mask[7] = {
    0u, 0x3fe0u, 0x3ffu, 0x1ffbfe00u, 0x7c000u, 0u, 0u
};
static const uint32_t pin_special_mask[7] = {
    0x8fc007e6u, 0xe3f3ffffu, 0x81ffffffu, 0xffffffffu,
    0xf00fc07fu, 1u, 0x189u
};
extern uint32_t g2_gpio_critical_save(void);           /* 0x473940 */

uint32_t g2_codec_pin_function(uint32_t pin, uint32_t config) {
    if (pin >= 224u)
        return 5u;
    uint32_t const bit = 1u << (pin & 31u);
    uint32_t const group = pin >> 5;
    if ((pin_function_mask[group] & bit) == 0u) {
        if (((config >> 10) & 3u) > 1u &&
            (pin_special_mask[group] & bit) == 0u)
            return 7u;
    } else {
        uint32_t const function = (config >> 13) & 7u;
        if (function != 0u && function != 6u && function != 1u)
            return 7u;
    }
    uint32_t const saved = g2_gpio_critical_save();
    *(volatile uint32_t *)(uintptr_t)0x40010400u = 0x73u;
    *(volatile uint32_t *)(uintptr_t)(0x40010000u + pin * 4u) = config;
    *(volatile uint32_t *)(uintptr_t)0x40010400u = 0u;
    __asm__ volatile("msr PRIMASK, %0" :: "r"(saved) : "memory");
    return 0u;
}
