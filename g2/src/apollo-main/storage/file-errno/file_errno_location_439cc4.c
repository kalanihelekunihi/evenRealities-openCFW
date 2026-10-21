/* Stock Main __errno-location pointer return at 0x439cc4. */
#include <stdint.h>
extern volatile uint32_t audio_uart_ring_errno_20074f14;
int32_t *audio_file_errno_location_439cc4(void)
{
    return (int32_t *)(void *)&audio_uart_ring_errno_20074f14;
}
