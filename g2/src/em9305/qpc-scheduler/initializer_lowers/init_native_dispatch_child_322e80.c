#include <stdint.h>

/* Native 0x322e80..0x322f06: report LL event 0x2c (BIG sync established)
 * for a BIG record: {u16 handle, 0x2c, status, status, handle, ...}. On
 * success it adds the transport latency (+44), NSE/BN (+25/+24), max PDU
 * (+26), ISO interval (+4), the scaled sync delay (+16 x 0x1a36e3 / 2^31)
 * and the handles (+2 of each of the four BIS objects at +56..) with
 * their count. */
extern void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);

uint32_t opencfw_em9305_dispatch_child_322e80(uintptr_t big, uint32_t status)
{
    uint8_t event[32] __attribute__((aligned(4)));
    (void)opencfw_em9305_memset(&event[4],0u,0x1cu);
    uint32_t handle=*(volatile uint8_t *)(big+2u);
    event[4]=(uint8_t)status;
    event[3]=(uint8_t)status;
    event[2]=0x2cu;
    event[5]=(uint8_t)handle;
    *(uint16_t *)&event[0]=(uint16_t)handle;
    if(status==0u){
        uint32_t delay=*(volatile uint32_t *)(big+16u);
        uint32_t latency=*(volatile uint32_t *)(big+44u);
        uint32_t nse=*(volatile uint8_t *)(big+25u);
        uint32_t bn=*(volatile uint8_t *)(big+24u);
        uint32_t max_pdu=*(volatile uint16_t *)(big+26u);
        uint32_t interval=*(volatile uint16_t *)(big+4u);
        uint32_t scaled=(uint32_t)(((uint64_t)delay*0x1a36e3u)>>31);
        *(uint32_t *)&event[8]=latency;
        event[12]=(uint8_t)nse;
        event[13]=(uint8_t)bn;
        *(uint16_t *)&event[14]=(uint16_t)max_pdu;
        *(uint16_t *)&event[16]=(uint16_t)interval;
        *(uint16_t *)&event[18]=(uint16_t)scaled;
        uint32_t count=0u;
        for(uint32_t index=0u;index<4u;++index){
            uintptr_t bis=*(volatile uint32_t *)(big+56u+index*4u);
            if(bis==0u)continue;
            *(uint16_t *)&event[22u+(uint8_t)count*2u]=*(volatile uint16_t *)(bis+2u);
            ++count;
        }
        event[20]=(uint8_t)count;
    }
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}
