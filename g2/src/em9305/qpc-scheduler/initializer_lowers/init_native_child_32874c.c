#include <stdint.h>

/* Native 0x32874c..0x3287b8: build a type-7 stream PDU for the record:
 * write the fixed stream header (0x33446c) and the 8-byte record built
 * from the global words 0x805aa0/0x805aa4 with length +32 plus 6, queue
 * it, mirror the two words and the length into the record's stream block
 * (+180: +100/+104 and +96), set bit 0 of flags byte +272 and clear the
 * pending byte +176 of the attached object. */
extern const uint8_t opencfw_em9305_stream_header_33446c[4];
extern uint32_t opencfw_em9305_child_3172c8(uint32_t kind);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_ll_stream_header_3175d0(uintptr_t output,
                                                       uintptr_t fields);
extern uint32_t opencfw_em9305_child_317594(uintptr_t out,uint32_t word,
                                            uint32_t type,uint32_t half);
extern uint32_t opencfw_em9305_child_3172dc(uintptr_t record,uintptr_t payload,
                                            uint32_t flags);

void opencfw_em9305_child_32874c(uintptr_t record)
{
    uintptr_t buffer=opencfw_em9305_child_3172c8(7u);
    if(buffer==0u)return;
    _Alignas(4) uint8_t fields[4];
    uint32_t length=*(volatile uint16_t *)(record+32u);
    (void)opencfw_em9305_memcpy(fields,opencfw_em9305_stream_header_33446c,4u);
    uintptr_t block=record+180u;
    uint32_t used=opencfw_em9305_ll_stream_header_3175d0(buffer,(uintptr_t)fields);
    uint32_t second=*(volatile uint32_t *)0x805aa4u;
    uint32_t first=*(volatile uint32_t *)0x805aa0u;
    length+=6u;
    (void)opencfw_em9305_child_317594(used+buffer,first,second,(uint16_t)length);
    (void)opencfw_em9305_child_3172dc(record,buffer,6u);
    second=*(volatile uint32_t *)0x805aa4u;
    uintptr_t object=*(volatile uint32_t *)block;
    *(volatile uint32_t *)(block+104u)=second;
    uint32_t flags=*(volatile uint8_t *)(record+272u);
    first=*(volatile uint32_t *)0x805aa0u;
    *(volatile uint16_t *)(block+96u)=(uint16_t)length;
    *(volatile uint32_t *)(block+100u)=first;
    *(volatile uint8_t *)(record+272u)=(uint8_t)(flags|1u);
    if(object!=0u)*(volatile uint8_t *)(object+176u)=0u;
}
