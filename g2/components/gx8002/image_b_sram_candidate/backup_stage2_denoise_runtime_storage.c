/* Native mode initialization names three disjoint BSS regions: the 28-byte
 * mode prefix at 0x2002d2bc, a five-word LVP_QUEUE at 0x2002d2d8, and a
 * 40-byte queue buffer at 0x2002d2f0. The four bytes between queue and
 * buffer are intentionally not attributed to any of these objects. */
#include <stdint.h>

volatile uint8_t gx8002_image_b_denoise_mode_state_2002d2bc[28]
    __attribute__((section(".bss.image_b_denoise_mode_prefix"), used, aligned(4)));

volatile int32_t gx8002_image_b_denoise_ring_2002d2d8[5]
    __attribute__((section(".bss.image_b_denoise_queue"), used, aligned(4)));

volatile uint8_t gx8002_image_b_denoise_queue_buffer_2002d2f0[40]
    __attribute__((section(".bss.image_b_denoise_queue_buffer"), used, aligned(4)));
