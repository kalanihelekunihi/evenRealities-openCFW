/* Native stage2 0x10003404 loads this single BSS word. The source does not
 * invent its retained-path producer or a warm initial value. */
#include <stdint.h>

volatile uint32_t gx8002_image_b_clock_gate_bits_20017394
    __attribute__((section(".bss.image_b_clock_gate_bits"), used, aligned(4)));
