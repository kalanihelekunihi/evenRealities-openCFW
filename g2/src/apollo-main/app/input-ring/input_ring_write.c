/* Native input ring write wrapper/core/free-space helpers
 * 0x46d8c4, 0x46d8e0, and 0x46da92. Descriptor words are
 * buffer, capacity, read index, write index, and callback. */
#include <stdint.h>

typedef void (*input_ring_callback)(void *,uint32_t,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */

/* Stock 0x46DA92 (lwrb_get_free) */
uint32_t audio_uart_input_ring_free(const void *descriptor) {
    if(descriptor==0) return 0u;
    const uint32_t *d=(const uint32_t *)descriptor;
    if(d[0]==0u || d[1]==0u) return 0u;
    uint32_t distance=(d[3]<d[2]) ? (0u-d[3]) : (d[1]-d[3]);
    return d[2]+distance-1u;
}

/* Stock 0x46D8E0 (lwrb_write_ex) */
uint32_t audio_uart_input_ring_write_core(void *descriptor,
                                           const void *source,uint32_t length,
                                           uint32_t *written,uint32_t strict) {
    if(descriptor==0 || source==0 || length==0u) return 0u;
    uint32_t *d=(uint32_t *)descriptor;
    if(d[0]==0u || d[1]==0u) return 0u;
    uint32_t free_bytes=audio_uart_input_ring_free(descriptor);
    if(free_bytes==0u || (free_bytes<length && (strict&1u)!=0u))
        return 0u;
    if(free_bytes<length) length=free_bytes;
    uint32_t first=length;
    if(d[1]-d[3]<length) first=d[1]-d[3];
    (void)audio_queue_copy_bytes((void *)(uintptr_t)(d[0]+d[3]),source,first);
    uint32_t second=length-first;
    uint32_t end=d[3]+first;
    if(second!=0u) {
        (void)audio_queue_copy_bytes((void *)(uintptr_t)d[0],
                                     (const uint8_t *)source+first,second);
        end=second;
    }
    if(end>=d[1]) end=0u;
    d[3]=end;
    if(d[4]!=0u)
        ((input_ring_callback)(uintptr_t)d[4])(descriptor,1u,length);
    if(written!=0) *written=length;
    return 1u;
}

/* Stock 0x46D8C4 (lwrb_write) */
uint32_t audio_uart_input_ring_write(void *descriptor,const void *source,
                                      uint32_t length) {
    uint32_t written=0u;
    if(audio_uart_input_ring_write_core(descriptor,source,length,&written,0u)==0u)
        return 0u;
    return written;
}
