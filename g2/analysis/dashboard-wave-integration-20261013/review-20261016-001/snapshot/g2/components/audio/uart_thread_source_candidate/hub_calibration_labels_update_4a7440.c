/* Native hub_calibration_labels_update 0x4a7440..0x4a7472. */
#include <stdint.h>

extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44120e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44121c(uint32_t, uint32_t, uint32_t);

void audio_uart_hub_calibration_labels_update_4a7440(uint32_t object,
                                                       uint32_t first,
                                                       uint32_t second) {
    audio_uart_page_44122a(object, first, second);
    audio_uart_page_441238(object, first, second);
    audio_uart_page_44120e(object, first, second);
    audio_uart_page_44121c(object, first, second);
}
