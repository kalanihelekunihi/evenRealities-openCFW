#include <stdint.h>

/* Native 0x3225b0..0x322618: commit a PAwR response descriptor. Copy the
 * source descriptor's (object +92) length/word/halfword/word fields
 * (+120/+124/+128/+132) into the context's current descriptor (context =
 * object +780, descriptor = context +428, re-read for each store), store
 * the value at context +396 and the source start (+112 plus +144) at
 * context +392, copy the 76-byte descriptor body over the first-read
 * descriptor, tag it 15 with the context byte +20 and insert the context
 * schedule entry (+384). */
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,
                                                                 uintptr_t tie);

static inline uintptr_t descriptor(uintptr_t context)
{ return *(volatile uint32_t *)(context+428u); }

uint32_t opencfw_em9305_callback_3225b0(uintptr_t object,uint32_t value)
{
    uintptr_t source=*(volatile uint32_t *)(object+92u);
    uintptr_t context=*(volatile uint32_t *)(object+780u);
    uint32_t length=*(volatile uint16_t *)(source+120u);
    uintptr_t target=descriptor(context);
    uint32_t word=*(volatile uint32_t *)(source+124u);
    *(volatile uint32_t *)(context+396u)=value;
    *(volatile uint16_t *)(target+120u)=(uint16_t)length;
    uintptr_t current=descriptor(context);
    uint32_t offset=*(volatile uint32_t *)(source+144u);
    *(volatile uint32_t *)(current+124u)=word;
    uint32_t half=*(volatile uint16_t *)(source+128u);
    current=descriptor(context);
    *(volatile uint16_t *)(current+128u)=(uint16_t)half;
    current=descriptor(context);
    uint32_t start=*(volatile uint32_t *)(source+112u);
    uint32_t last=*(volatile uint32_t *)(source+132u);
    *(volatile uint32_t *)(context+392u)=start+offset;
    *(volatile uint32_t *)(current+132u)=last;
    (void)opencfw_em9305_memcpy((void *)target,
                                (const void *)*(volatile uint32_t *)(object+92u),76u);
    uintptr_t fresh=*(volatile uint32_t *)(object+780u);
    *(volatile uint8_t *)target=15u;
    *(volatile uint8_t *)(target+1u)=*(volatile uint8_t *)(fresh+20u);
    return opencfw_em9305_associated_schedule_insert_312da4(context+384u,0u);
}
