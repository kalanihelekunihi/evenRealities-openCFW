/* Apollo S200 Nema buffer creator adapter at 0x53cf78. */
#include <stdint.h>

extern void audio_uart_nema_buffer_create_514070(uint32_t *,uint32_t,
                                                   uint32_t);

uint32_t audio_uart_ambiq_buffer_base_53cf78(uint32_t pool,
                                               uint32_t size,
                                               uint32_t ignored) {
    (void)ignored;
    uint32_t descriptor[4];
    audio_uart_nema_buffer_create_514070(descriptor,pool,size);
    return descriptor[2];
}
