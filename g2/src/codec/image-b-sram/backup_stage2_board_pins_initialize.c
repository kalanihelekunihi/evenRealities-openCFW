/* Native image-B 0x10008978..0x100089d6. The 13 pin/function pairs
 * reproduce the typed board configuration at native 0x10012ecc, including
 * the special pin-2/function-0 branch. Lower pin programming and final
 * validation remain genuine callable contracts.
 */
#include <stdint.h>

struct gx8002_image_b_pin_mode {
    uint8_t pin;
    uint8_t function;
};

static const struct gx8002_image_b_pin_mode board_pins[13] = {
    {0u, 1u}, {1u, 1u}, {2u, 0u}, {3u, 1u}, {4u, 1u},
    {5u, 1u}, {6u, 1u}, {7u, 1u}, {8u, 1u}, {9u, 1u},
    {10u, 1u}, {11u, 1u}, {12u, 1u}
};

extern int32_t gx8002_image_b_pin_options_10008770(
    const struct gx8002_image_b_pin_mode *, int32_t);
extern int32_t gx8002_image_b_pin_check_100086dc(uint32_t, uint32_t);
extern uint32_t gx8002_image_b_spi_pin_mode_10008154(uint32_t, uint32_t);
extern void gx8002_image_b_board_pins_finish_100088cc(void);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);
extern volatile uint32_t gx8002_image_b_board_pins_ready_200176d8;

void gx8002_image_b_rtc_tick_initialize_10008978(void)
{
    (void)gx8002_image_b_pin_options_10008770(board_pins, 13);
    for (uint32_t i = 0u; i < 13u; ++i) {
        uint32_t pin = board_pins[i].pin;
        uint32_t function = board_pins[i].function;
        if (gx8002_image_b_pin_check_100086dc(pin, function) != 0)
            (void)gx8002_image_b_heap_log_10009934(
                "pin %d set error!\n", pin);
        if (function == 1u || (pin == 2u && function == 0u))
            (void)gx8002_image_b_spi_pin_mode_10008154(pin, 0u);
    }
    gx8002_image_b_board_pins_finish_100088cc();
    gx8002_image_b_board_pins_ready_200176d8 = 1u;
}
