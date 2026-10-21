/* Apollo hand record at native RAM 0x200736d4, within startup zero range.
 * Final absolute placement is a product linker requirement, not set here. */
#include <stdint.h>

uint8_t audio_uart_hand_record[0x30u];

/* The native ROM pointer literal at 0x4667ec resolves to the same record. */
const volatile uint8_t *const audio_uart_hand_context = audio_uart_hand_record;
