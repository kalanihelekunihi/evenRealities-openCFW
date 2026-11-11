#include <stdint.h>

/* Native 0x32387c..0x3239b6: compose the advertising PDU for the record's
 * event type (+32, low three bits). Connectable/scannable legacy types
 * (1, 2, 5, 6) allow the TxAdd bit 0x40 for a random own address (+61);
 * type 0 (and 4, extended) derive the header flags from the advertising
 * data length (+2250), own address type and directed mode (+369 with
 * +2786), forcing the extended header when the payload is empty or
 * directed, otherwise limiting it to the plain (|1) or extended (|3)
 * forms; with privacy (bit 5 of 0x805a85) the address flags are masked.
 * A 5-byte header (7, then zeros) is filled by children 318440 and
 * 3184f4 from the request block (+2312), the reject byte +827 is cleared
 * and the PDU is composed into output with count. */
extern uint32_t opencfw_em9305_child_318440(uintptr_t link,uintptr_t params,
                                            uintptr_t request);
extern void opencfw_em9305_child_3184f4(uintptr_t out,uintptr_t link,
                                        uintptr_t request);
extern uint32_t opencfw_em9305_radio_compose_323dc0(uintptr_t record,
    uint32_t forced,uint32_t allowed,uint32_t prefix,uintptr_t header,
    uintptr_t source,uintptr_t output,uint32_t type,uint32_t count);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}

uint32_t opencfw_em9305_child_32387c(uintptr_t record,uintptr_t output,
                                     uint32_t count)
{
    _Alignas(4) uint8_t header[8];
    uint32_t kind=r16(record+32u)&7u;
    uint32_t allowed=0u,forced=0u;
    header[0]=7u;
    header[4]=0u;
    header[3]=0u;
    header[2]=0u;
    header[1]=0u;
    if(kind==1u||kind==2u||kind==5u||kind==6u){
        forced=0x18u;
        allowed=(uint32_t)(r8(record+61u)==1u)<<6;
    }else if(kind==0u||kind==4u){
        uint32_t length=r16(record+2250u);
        uint32_t random=r8(record+61u)==1u;
        uint32_t empty=length==0u;
        uint32_t directed=r8(record+369u);
        forced=empty?0u:0x18u;
        if(kind==0u)allowed=(empty<<6)|random|(random<<6);
        else allowed=random|(empty<<6)|(random<<1)|(random<<6);
        if(directed!=0u&&r8(record+2786u)==0u)forced=0x18u;
        if((forced&0x10u)!=0u){
            if((r8(0x805a85u)&0x20u)!=0u)
                allowed&=kind==0u?~0x3fu:~0x3du;
        }else{
            forced|=kind==0u?1u:3u;
        }
    }
    uintptr_t request=record+0x908u;
    if((forced&0x10u)!=0u)allowed&=0xbfu;
    (void)opencfw_em9305_child_318440((uintptr_t)header,request,record);
    opencfw_em9305_child_3184f4((uintptr_t)header,request,record);
    uint32_t prefix=r16(record+32u)&3u;
    *(volatile uint8_t *)(record+827u)=0u;
    return opencfw_em9305_radio_compose_323dc0(record,forced,(uint8_t)allowed,
        prefix,(uintptr_t)header,0u,output,0u,count);
}
