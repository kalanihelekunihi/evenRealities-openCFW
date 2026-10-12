/* Native stage2 clears exactly 360 bytes and iterates ten 36-byte records
 * starting at 0x200174bc. The conditional BSS reset remains authoritative. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_timer_records_200174bc[90]
    __attribute__((section(".bss.image_b_timer_records"), used, aligned(4)));
