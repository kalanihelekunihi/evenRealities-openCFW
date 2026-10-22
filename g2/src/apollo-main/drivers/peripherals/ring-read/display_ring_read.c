/* Native ring count/read 0x46dacc/0x46d9c8 and wrapper 0x46d9ac.
 * The wrapper passes strict=0 and returns the number of bytes copied. */
#include <stdint.h>
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
typedef void (*ring_callback)(void *,uint32_t,uint32_t);
/* Stock 0x46DACC (lwrb_get_full) */
uint32_t audio_uart_display_ring_available(const void *descriptor) {
    if(descriptor==0) return 0u;
    const uint32_t *d=(const uint32_t *)descriptor;
    if(d[0]==0u||d[1]==0u) return 0u;
    uint32_t read=d[2],write=d[3];
    return write<read?write+(d[1]-read):write-read;
}
/* Stock 0x46D9AC (lwrb_read) */
uint32_t audio_uart_display_ring_read(void *descriptor,void *destination,
                                       uint32_t count) {
    uint32_t *d=(uint32_t *)descriptor;
    if(d==0||d[0]==0u||d[1]==0u||destination==0||count==0u)
        return 0u;
    uint32_t available=audio_uart_display_ring_available(d);
    if(available==0u) return 0u;
    if(count>available) count=available;
    uint32_t first=count;
    if(d[1]-d[2]<first) first=d[1]-d[2];
    (void)audio_queue_copy_bytes(destination,
                                 (const void *)(uintptr_t)(d[0]+d[2]),first);
    uint32_t remainder=count-first;
    uint32_t next=d[2]+first;
    if(remainder!=0u) {
        (void)audio_queue_copy_bytes((uint8_t *)destination+first,
                                     (const void *)(uintptr_t)d[0],remainder);
        next=remainder;
    }
    if(next>=d[1]) next=0u;
    d[2]=next;
    if(d[4]!=0u)
        ((ring_callback)(uintptr_t)d[4])(d,0u,count);
    return count;
}
