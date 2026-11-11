#include <stdint.h>

/* Native 0x3287b8..0x328812: build a stream PDU for the record: allocate
 * a type-3 buffer, write the fixed stream header (0x334470) with the
 * record byte +290 and length +32 plus 6, queue it on the record, store
 * the new length at +288 and set bit 1 of flags byte +272. Always send
 * status message 3 for the record. */
extern const uint8_t opencfw_em9305_stream_header_334470[4];
extern uint32_t opencfw_em9305_child_3172c8(uint32_t kind);
extern void *opencfw_em9305_memcpy(void *destination,const void *source,
                                   uint32_t bytes);
extern uint32_t opencfw_em9305_ll_stream_header_3175d0(uintptr_t output,
                                                       uintptr_t fields);
extern uint32_t opencfw_em9305_child_3175bc(uint32_t a,uint32_t b,uint32_t c);
extern uint32_t opencfw_em9305_child_3172dc(uintptr_t record,uintptr_t payload,
                                            uint32_t flags);
extern uint32_t opencfw_em9305_child_329064(uintptr_t record,uint32_t status);

uint32_t opencfw_em9305_child_3287b8(uintptr_t record)
{
    uintptr_t buffer=opencfw_em9305_child_3172c8(3u);
    if(buffer!=0u){
        _Alignas(4) uint8_t fields[4];
        uint32_t length=*(volatile uint16_t *)(record+32u);
        (void)opencfw_em9305_memcpy(fields,opencfw_em9305_stream_header_334470,4u);
        uint32_t used=opencfw_em9305_ll_stream_header_3175d0(buffer,(uintptr_t)fields);
        length+=6u;
        (void)opencfw_em9305_child_3175bc(used+buffer,
                                          *(volatile uint8_t *)(record+290u),
                                          (uint16_t)length);
        (void)opencfw_em9305_child_3172dc(record,buffer,6u);
        uint32_t flags=*(volatile uint8_t *)(record+272u);
        *(volatile uint16_t *)(record+288u)=(uint16_t)length;
        *(volatile uint8_t *)(record+272u)=(uint8_t)(flags|2u);
    }
    return opencfw_em9305_child_329064(record,3u);
}
