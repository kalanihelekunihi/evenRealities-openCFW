/* Native image-B board pin transition 0x1000888c..0x10008972.
 * Before the ready word is set, 0x888c checks the configured pin function;
 * after initialization it writes directly. The stock validation failure
 * prints, resets four pins, and loops forever. No substitute trap is used.
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_board_pins_ready_200176d8;
extern int32_t gx8002_image_b_pin_check_100086dc(uint32_t, uint32_t);
extern int32_t gx8002_image_b_pinmux_write_10008720(uint32_t, uint32_t);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

int32_t gx8002_image_b_board_pin_apply_1000888c(uint32_t pin,
                                                  uint32_t function)
{
    if (gx8002_image_b_board_pins_ready_200176d8 == 0u &&
        gx8002_image_b_pin_check_100086dc(pin, pin != 2u) != 0) {
        (void)gx8002_image_b_heap_log_10009934(
            "pin %d function conflict !\n", pin);
        return -1;
    }
    (void)gx8002_image_b_pinmux_write_10008720(pin, function);
    return 0;
}

void gx8002_image_b_board_pins_finish_100088cc(void)
{
    static const struct { uint8_t pin; uint8_t function; } plan[12] = {
        {0u, 7u}, {1u, 7u}, {3u, 0u}, {4u, 0u},
        {5u, 0u}, {6u, 0u}, {11u, 0u}, {12u, 0u},
        {7u, 3u}, {8u, 3u}, {9u, 3u}, {10u, 3u}
    };
    int32_t errors = 0;
    for (uint32_t i = 0u; i < 12u; ++i)
        errors += gx8002_image_b_board_pin_apply_1000888c(
            plan[i].pin, plan[i].function);
    if (errors == 0)
        return;
    (void)gx8002_image_b_pinmux_write_10008720(5u, 0u);
    (void)gx8002_image_b_pinmux_write_10008720(6u, 0u);
    (void)gx8002_image_b_pinmux_write_10008720(11u, 0u);
    (void)gx8002_image_b_pinmux_write_10008720(12u, 0u);
    (void)gx8002_image_b_heap_log_10009934(
        "!!!pin set error!\n Please check Board Options!!!");
    for (;;) {
    }
}
