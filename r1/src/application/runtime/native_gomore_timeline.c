#include <stdint.h>

uint32_t r1_gomore_packed_sample_get_native(const volatile uint8_t *data,uint32_t index)
{
    index%=2880u;
    return (data[index>>2]>>((index&3u)*2u))&3u;
}

/* ARM register LSL uses the low byte of the count, and yields zero at >=32. */
static uint32_t register_lsl(uint32_t value,uint32_t shift)
{ shift&=255u;return shift<32u ? value<<shift : 0; }

uint32_t r1_gomore_packed_sample_set_native(uint32_t value,volatile uint8_t *data,int32_t index)
{
    int32_t remainder=index%2880;
    int32_t offset=remainder/4;
    uint32_t shift=(uint32_t)(remainder-offset*4)*2u;
    uint32_t mask=register_lsl(3,shift);
    uint32_t shifted=register_lsl(value,shift);
    data[offset]=(uint8_t)(((uint32_t)data[offset]&~mask)|shifted);
    return shifted;
}

int32_t r1_gomore_packed_timeline_extract_native(uint32_t context,uint32_t start,
        uint32_t end,uint32_t clear_end,uint32_t unused,uint32_t clear_start,
        uint32_t alternate_clear_end,uint32_t output)
{
    (void)unused;
    if (!output) return 0;
    volatile uint8_t *data=(volatile uint8_t *)(uintptr_t)context;
    volatile uint8_t *dest=(volatile uint8_t *)(uintptr_t)output;
    if (clear_end-start<=900u) {
        for (uint32_t t=start;t<clear_end;t+=30u) {
            uint32_t slot=t/30u;
            if (r1_gomore_packed_sample_get_native(data,slot))
                r1_gomore_packed_sample_set_native(0,data,(int32_t)slot);
        }
    } else if (clear_start) {
        for (uint32_t t=clear_start;t<alternate_clear_end;t+=30u) {
            uint32_t slot=t/30u;
            if (r1_gomore_packed_sample_get_native(data,slot))
                r1_gomore_packed_sample_set_native(0,data,(int32_t)slot);
        }
    }
    uint32_t count=0;
    /* The stock stride selector is initialized to one and never changed. */
    while (start<end) {
        dest[count++]=(uint8_t)r1_gomore_packed_sample_get_native(data,start/30u);
        if (count>=2880u) break;
        start+=30u;
    }
    return (int32_t)count;
}
