/* Apollo Nema 3x3 matrix copy at 0x561830..0x561854. */
#include <stdint.h>

void audio_uart_nema_matrix_copy_561830(void *destination,
                                        const void *source) {
    volatile uint32_t *const dst=(volatile uint32_t *)destination;
    const volatile uint32_t *const src=(const volatile uint32_t *)source;
    for (uint32_t index=0;index<9u;++index) dst[index]=src[index];
}
