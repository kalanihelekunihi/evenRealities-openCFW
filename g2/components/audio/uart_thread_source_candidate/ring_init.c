/* Native ring initializer 0x57e3a4..0x57e3d7 and compiler memset ABI
 * at 0x43c0e4. The native helper takes (destination,length,fill). */
#include <stdint.h>
void audio_uart_buffer_zero(void *destination,uint32_t length,uint32_t fill)
{
    volatile uint8_t *p=(volatile uint8_t *)destination;
    for (uint32_t i=0;i<length;i++) p[i]=(uint8_t)fill;
}
void audio_uart_transport_initialize(void *descriptor,void *storage,uint32_t capacity,
                                     uint32_t element_bytes,uint32_t mode,uint32_t arg5,uint32_t arg6)
{
    (void)arg5;(void)arg6;
    uint8_t *d=(uint8_t *)descriptor;
    audio_uart_buffer_zero(storage,capacity,0x55u);
    audio_uart_buffer_zero(d,36u,0u);
    *(uint32_t *)(d+24u)=(uint32_t)(uintptr_t)storage;
    *(uint32_t *)(d+8u)=capacity;
    *(uint32_t *)(d+12u)=element_bytes;
    d[28u]=(uint8_t)mode;
}
