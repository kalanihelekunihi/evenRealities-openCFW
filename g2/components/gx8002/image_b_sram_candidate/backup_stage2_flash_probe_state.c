/* Source-owned native flash probe state byte at 0x2001765c.
 * The stage-2 CRT clears its containing interval only on the cold path;
 * this NOLOAD object has no invented initializer on retained startup.
 */
#include <stdint.h>
volatile uint8_t gx8002_image_b_flash_probe_state_2001765c
    __attribute__((section(".bss.image_b_flash_probe_state"), used, aligned(1)));
