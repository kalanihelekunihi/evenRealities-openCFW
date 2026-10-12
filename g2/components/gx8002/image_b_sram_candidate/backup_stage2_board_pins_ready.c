/* Native image-B word at 0x200176d8, read by board_pin_apply and set to 1
 * by rtc_tick_initialize. Its containing BSS is cleared only on cold boot. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_board_pins_ready_200176d8
    __attribute__((section(".bss.image_b_board_pins_ready"), used, aligned(4)));
