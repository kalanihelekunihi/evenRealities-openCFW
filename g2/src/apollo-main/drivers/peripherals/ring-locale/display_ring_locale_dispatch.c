/* Native locale dispatch wrappers 0x4d58ae/0x4d58c2 and range error
 * writer 0x439cb2. The accessed callback slots are initialized from
 * authenticated RAM and have C-owned ASCII callback implementations. */
#include <stdint.h>
#include "display_ring_locale_dispatch_table.h"
extern volatile uint32_t audio_uart_ring_errno_20074f14;
int32_t audio_uart_ring_locale_space_4d58ae(uint32_t value) {
    return (int32_t)audio_uart_ring_locale_dispatch_200044c0.space(value);
}
int32_t audio_uart_ring_locale_lower_4d58c2(uint32_t value) {
    return (int32_t)audio_uart_ring_locale_dispatch_200044c0.lower(value);
}
void audio_uart_ring_errno_range_set_439cb2(void) {
    audio_uart_ring_errno_20074f14=0x22u;
}
