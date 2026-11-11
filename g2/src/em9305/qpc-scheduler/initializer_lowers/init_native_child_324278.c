#include <stdint.h>

/* Native 0x324278..0x324352: build an advertising PDU header for the set
 * at record. Runs the 318440/3184f4 option steps on an 8-byte header
 * frame, picks the PDU type from the event properties (+32 & 7: 2 -> 6,
 * 5 -> 1, 3 -> 0, else 2), writes AdvA (+16) at buf+2 and, for type 1,
 * TargetA (+24) at buf+8 (marking bit 2 of +2392). Types 0, 2 and 6 then
 * append up to 31 bytes of advertising data (+1441 length, +1442 data).
 * Bit 6 of 0x805a95 marks ChSel for types 0/1. The payload length is
 * encoded with 3239d4; returns length + 2. */
extern uint32_t opencfw_em9305_child_318440(uintptr_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_child_3184f4(uintptr_t,uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t length);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t,uintptr_t);

uint32_t opencfw_em9305_child_324278(uintptr_t record, uintptr_t buffer)
{
    uint8_t header[8] __attribute__((aligned(4)));
    uintptr_t options=record+2312u;
    *(uint32_t *)header=0u;
    header[4]=0u;
    (void)opencfw_em9305_child_318440((uintptr_t)header,options,record);
    (void)opencfw_em9305_child_3184f4((uintptr_t)header,options,record);
    uint32_t properties=*(volatile uint16_t *)(record+32u)&7u;
    uintptr_t start=buffer+2u;
    if(properties==2u)header[0]=6u;
    else if(properties==5u)header[0]=1u;
    else if(properties==3u)header[0]=0u;
    else header[0]=2u;
    (void)opencfw_em9305_radio_address_write_3045e8(start,*(volatile uint32_t *)(record+16u),
                                                     *(volatile uint32_t *)(record+20u));
    uint32_t type=*(volatile uint8_t *)header;
    uintptr_t end=buffer+8u;
    if(type==1u){
        *(volatile uint32_t *)(record+2392u)|=4u;
        (void)opencfw_em9305_radio_address_write_3045e8(end,*(volatile uint32_t *)(record+24u),
                                                         *(volatile uint32_t *)(record+28u));
        type=*(volatile uint8_t *)header;
        end=buffer+14u;
    }
    uint32_t data_length=0u;
    if(type<7u&&((0x45u>>type)&1u)!=0u){
        uint32_t length=*(volatile uint8_t *)(record+1441u);
        if(length!=0u){
            (void)opencfw_em9305_memcpy((void *)end,(const void *)(record+1442u),
                                        length<31u?length:31u);
            data_length=length;
        }
    }
    if((*(volatile uint8_t *)(uintptr_t)0x805a95u&0x40u)!=0u&&type<2u)header[1]=1u;
    header[4]=(uint8_t)(end-start+data_length);
    (void)opencfw_em9305_radio_encode_3239d4(buffer,(uintptr_t)header);
    return (uint8_t)(*(volatile uint8_t *)&header[4]+2u);
}
