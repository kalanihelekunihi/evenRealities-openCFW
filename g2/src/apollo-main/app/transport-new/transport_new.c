/* Native ring transport constructor 0x57df7c..0x57e027. */
#include <stdint.h>
extern void offline_assert(void) __attribute__((noreturn));
extern void audio_uart_transport_initialize(void *descriptor,void *storage,uint32_t capacity,
                                           uint32_t element_bytes,uint32_t mode,uint32_t arg5,uint32_t arg6);
/* Child 0x57e3a4 has seven ABI arguments; these types preserve register/stack layout. */
void *audio_uart_transport_new(uint32_t capacity,uint32_t element_bytes,uint32_t selectable,
                               void *storage,void *descriptor,uint32_t arg5,uint32_t arg6)
{
    if (!storage || !descriptor || capacity<element_bytes || capacity<5u)
        offline_assert();
    if (element_bytes==0u) element_bytes=1u;
    uint32_t mode=selectable ? 3u : 2u;
    audio_uart_transport_initialize(descriptor,storage,capacity,element_bytes,mode,arg5,arg6);
    ((uint8_t *)descriptor)[28u]|=2u;
    return descriptor;
}
