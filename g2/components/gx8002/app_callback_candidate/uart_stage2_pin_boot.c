/* SPDX-License-Identifier: MIT
 * Stage-2 pin setup at direct native 0x10005434. The thirteen
 * pin/value pairs at stock 0x100082e0 and format at 0x100082fc
 * are semantic source-owned initialized data.
 */
#include <stdint.h>

struct pin_start_value { uint8_t pin; uint8_t value; };
_Static_assert(sizeof(struct pin_start_value) == 2, "pin/value ABI");

__attribute__((section(".stage2.pin.initial"), used))
static const struct pin_start_value initial_pins[13] = {
    {0,0}, {1,0}, {2,0}, {3,0}, {4,0}, {5,0}, {6,0},
    {7,0}, {8,0}, {9,0}, {10,0}, {11,0}, {12,0},
};
static const char pin_error_format[] = "pin %d set error!\n";

extern uint32_t gx8002_uart_stage2_pin_prepare_5094(
    const struct pin_start_value *pins, uint32_t count);
extern uint32_t gx8002_uart_stage2_pin_matches_5000(uint32_t pin,
                                                       uint32_t value);
extern int32_t gx8002_uart_stage2_launch_61a4(const char *format, ...);

void gx8002_uart_stage2_setup_5434(void)
{
    (void)gx8002_uart_stage2_pin_prepare_5094(initial_pins, 13u);
    for (uint32_t i = 0; i < 13u; ++i) {
        if (gx8002_uart_stage2_pin_matches_5000(initial_pins[i].pin,
                                              initial_pins[i].value) != 0)
            gx8002_uart_stage2_launch_61a4(pin_error_format,
                                             (int32_t)initial_pins[i].pin);
    }
}
