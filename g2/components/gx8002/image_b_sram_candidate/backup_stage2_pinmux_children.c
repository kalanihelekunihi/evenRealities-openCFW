/* Native image-B pinmux 0x100086dc, 0x10008720, and 0x10008770.
 * The 31 default pin/function pairs at 0x10012e75 encode function zero
 * for pins 1..31. Pinned NationalChip Grus pinmux API corroborates four
 * bits per pin; the source below retains native MMIO readback behavior.
 */
#include <stdint.h>

struct gx8002_image_b_pin_mode {
    uint8_t pin;
    uint8_t function;
};

static volatile uint32_t *const pinmux =
    (volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010090);

int32_t gx8002_image_b_pin_check_100086dc(uint32_t pin,
                                             uint32_t function)
{
    if ((int32_t)pin < 0 || (int32_t)function < 0)
        return -1;
    if (pin >= 33u)
        return function == 255u ? 0 : -1;
    uint32_t shift = (pin & 7u) * 4u;
    uint32_t actual = (pinmux[pin >> 3] >> shift) & 15u;
    return actual == function ? 0 : -1;
}

int32_t gx8002_image_b_pinmux_write_10008720(uint32_t pin,
                                                uint32_t function)
{
    if (pin >= 33u)
        return -1;
    uint32_t shift = (pin & 7u) * 4u;
    volatile uint32_t *const register_word = pinmux + (pin >> 3);
    uint32_t previous = *register_word;
    uint32_t replacement = (previous & ~(15u << shift)) |
                           ((function & 15u) << shift);
    *register_word = replacement;
    if ((int32_t)function < 0)
        return -1;
    return (((*register_word >> shift) & 15u) == function) ? 0 : -1;
}

int32_t gx8002_image_b_pin_options_10008770(
    const struct gx8002_image_b_pin_mode *options, int32_t count)
{
    if (options == 0 || count < 0)
        return -1;
    for (uint32_t pin = 0u; pin < 32u; ++pin) {
        uint32_t function = 0u;
        for (int32_t i = 0; i < count; ++i) {
            if ((uint32_t)options[i].pin == pin) {
                function = options[i].function;
                break;
            }
        }
        (void)gx8002_image_b_pinmux_write_10008720(pin, function);
    }
    return 0;
}
