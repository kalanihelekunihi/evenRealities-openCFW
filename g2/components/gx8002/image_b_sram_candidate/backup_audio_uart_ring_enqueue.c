/* SPDX-License-Identifier: MIT
 * Image-B native 0x1000bde8..0x1000bdf5 ring enqueue wrapper.
 * Native literal at 0x1000bdf8 is 0x2002d784, inside the second
 * source-owned UART ring header initialized by 0x1000b5f8.
 * binh_b_stage2.bin SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_ring_write_10015b64(
    volatile int32_t *ring, const uint8_t *source);

int32_t gx8002_image_b_audio_uart_ring_enqueue_1000bde8(
    const uint8_t *source)
{
    gx8002_image_b_audio_ring_write_10015b64(
        (volatile int32_t *)(uintptr_t)UINT32_C(0x2002d784), source);
    return 0;
}
