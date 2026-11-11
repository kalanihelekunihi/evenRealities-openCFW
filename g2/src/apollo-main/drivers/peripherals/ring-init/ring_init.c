/* Native ring initializer 0x57e3a4..0x57e3d7 and compiler memset ABI
 * at 0x43c0e4. The native helper takes (destination,length,fill) and fills
 * from the end downwards; r0 is not consumed by callers (we return the
 * destination). Single implementation of stock 0x43c0e4: g2_lfs_cache_fill
 * g2_log_candidate_stack_fill and g2_log_stack_fill are aliases of this body. */
#include <stdint.h>
void *audio_uart_buffer_zero(void *destination,uint32_t length,uint32_t fill)
{
    volatile uint8_t *p=(volatile uint8_t *)destination;
    for (uint32_t i=length;i!=0u;--i) p[i-1u]=(uint8_t)fill;
    return destination;
}
__typeof__(audio_uart_buffer_zero) g2_lfs_cache_fill __attribute__((alias("audio_uart_buffer_zero")));
__typeof__(audio_uart_buffer_zero) g2_log_candidate_stack_fill __attribute__((alias("audio_uart_buffer_zero")));
__typeof__(audio_uart_buffer_zero) g2_log_stack_fill __attribute__((alias("audio_uart_buffer_zero")));
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
