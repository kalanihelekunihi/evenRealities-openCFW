/* Native memcpy wrapper 0x454738; lower 0x439be4 is already selected. */
#include <stdint.h>
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
void *audio_uart_lv_grid_copy_454738(void *destination,const void *source,uint32_t length)
{
    (void)audio_queue_copy_bytes(destination,source,length);
    return destination;
}
