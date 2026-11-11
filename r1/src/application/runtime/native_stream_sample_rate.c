/* Stock R1 0x7d0d8. Deliberately keep native 32-bit arithmetic and sequential
 * overlap-safe sample copies; a whole-buffer move changes aliased behavior. */
#include <stdint.h>
#include <stddef.h>
extern void *r1_native_memory_move(void *,const void *,size_t);
uint32_t r1_stream_sample_rate_copy(const void *source,uint32_t source_rate,uint32_t source_bytes,void *destination,uint32_t destination_rate,uint32_t sample_bytes)
{
    if (!source || !destination || !sample_bytes || !source_rate || !destination_rate) return 0;
    uint32_t available=source_bytes/sample_bytes;
    if (!available) return 0;
    if (available>source_rate) available=source_rate;
    uint32_t count=(available*destination_rate+(source_rate>>1))/source_rate;
    if (count>destination_rate) count=destination_rate;
    if (!count) return 0;
    for (uint32_t i=0;i<count;i++) {
        uint32_t index=(i*source_rate)/destination_rate;
        if (index>=available) index=available-1;
        uintptr_t from=(uint32_t)(uintptr_t)source+index*sample_bytes;
        uintptr_t to=(uint32_t)(uintptr_t)destination+i*sample_bytes;
        (void)r1_native_memory_move((void *)to,(const void *)from,sample_bytes);
    }
    return count*sample_bytes;
}
