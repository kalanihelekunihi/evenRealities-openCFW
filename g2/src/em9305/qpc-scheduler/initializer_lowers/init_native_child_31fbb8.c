#include <stdint.h>

/* Native 0x31fbb8..0x31fdc2: initialise the advertising set record for a
 * scannable/non-connectable start: clear the 240-byte block at +244,
 * install the scheduler and completion callbacks, the first channel
 * (325708), access address 0x8e89bed6, CRC init 0x555555 and the window
 * halfwords for the event properties (+14: 0xd7, 0x200 or 0x2d7 forms,
 * bit 1 sets header flag 0x20), allocate the 66-byte PDU buffer (+392,
 * 0x1f when none), take the own address (static 0x805b40 or public
 * 0x805a8c by bit 0 of +13, resolution flags 0x51 with 0x805a9d) and, for
 * a scannable set (+12 == 1), prepare the scan response (+114) and its
 * 39-byte buffer (+400; on failure the PDU buffer is released and 0x1f
 * returned). Finally schedule the first event (+256 = now + 1228, +260 =
 * interval +10 * 625) and register the role bit in the advertising masks
 * at 0x8019f8/0x8019fa, inserting the auxiliary entry when the role is the
 * first one. Returns 0. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern uint32_t opencfw_em9305_child_31fbac(uint32_t a);
extern uint32_t opencfw_em9305_child_31fdc4(uintptr_t owner);
extern uint32_t opencfw_em9305_init_channel_first_325708(uint32_t flags);
extern uint32_t opencfw_em9305_radio_completion_303fb8(uint32_t current,
    uint32_t first,uint32_t second,uint32_t third,uint32_t fourth,uint32_t fifth);
extern uint32_t opencfw_em9305_radio_completion_304140(uint32_t unused,
                                                       uint32_t second);
extern uint32_t opencfw_em9305_child_320f30(uintptr_t object,uint32_t now,
                                            uint32_t limit);
extern void opencfw_em9305_child_31f538(uintptr_t owner,uintptr_t pdu);
extern uint32_t opencfw_em9305_child_31f50c(uintptr_t record,uintptr_t command);
extern void opencfw_em9305_child_31f9ac(void);
extern uint32_t opencfw_em9305_child_31f904(uintptr_t owner,uintptr_t pdu);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern void opencfw_em9305_wsf_event_release(uintptr_t event);
extern uint32_t opencfw_em9305_scan_prepare_3243c0(uintptr_t output,
                                                   uintptr_t source);
extern uint32_t opencfw_em9305_scan_current_303f80(void);
extern uint32_t opencfw_em9305_auxiliary_insert_313220(uintptr_t object);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
#define CODE(f) ((uint32_t)(uintptr_t)(f))

uint32_t opencfw_em9305_child_31fbb8(uintptr_t set)
{
    uintptr_t schedule=set+244u;
    (void)opencfw_em9305_memset((void *)schedule,0u,240u);
    w32(set+288u,set+292u);
    uint32_t channels=r8(0x805b00u);
    w8(set+268u,3u);
    w32(set+276u,CODE(opencfw_em9305_child_31fbac));
    w32(set+272u,CODE(opencfw_em9305_child_31fdc4));
    w16(set+270u,257u);
    w8(set+292u,2u);
    w32(set+280u,set);
    uint32_t first=opencfw_em9305_init_channel_first_325708(channels);
    uint32_t role=r8(set+16u);
    uint32_t properties=r8(set+14u);
    w8(set+293u,first);
    w32(set+296u,0x8e89bed6u);
    uint32_t accuracy=r8(0x805a9cu);
    w32(set+300u,0x555555u);
    uint32_t kind=((role==2u)?2u:0u)+1u;
    w8(set+294u,accuracy);
    uint32_t window=(properties&4u)<<7;
    if((properties&8u)==0u)window|=0xd7u;
    w16(set+368u,0xd7u);
    w8(set+305u,kind);
    w8(set+304u,kind);
    if((properties&0xcu)!=0u)w16(set+368u,window);
    if((properties&1u)!=0u)w16(set+370u,window);
    if((properties&2u)!=0u)w32(set+372u,r32(set+372u)|0x20u);
    channels=r8(0x805b00u);
    w32(set+436u,CODE(opencfw_em9305_radio_completion_303fb8));
    w32(set+432u,CODE(opencfw_em9305_radio_completion_304140));
    w32(set+428u,CODE(opencfw_em9305_child_320f30));
    w32(set+412u,CODE(opencfw_em9305_child_31f538));
    w32(set+408u,CODE(opencfw_em9305_child_31f50c));
    w8(set+442u,0x42u);
    w8(set+443u,channels);
    uintptr_t buffer=opencfw_em9305_wsf_event_allocate(0x42u);
    w32(set+392u,buffer);
    if(buffer==0u)return 0x1fu;
    uint32_t options=r8(set+13u);
    w32(set+416u,CODE(opencfw_em9305_child_31f9ac));
    uint32_t header=r32(set+372u);
    uint32_t own_low,own_high;
    if((options&1u)!=0u){
        own_high=r32(0x805a90u);
        own_low=r32(0x805a8cu);
        header|=2u;
    }else{
        own_high=r32(0x805b44u);
        own_low=r32(0x805b40u);
    }
    uint32_t resolve=r8(0x805a9du);
    uint32_t value=header|1u;
    w32(set+376u,own_low);
    w32(set+380u,own_high);
    w32(set+372u,value);
    if(resolve!=0u){
        value=header|81u;
        w32(set+372u,value);
    }
    uint32_t scannable=r8(set+12u);
    uintptr_t response=0u;
    if(scannable==1u){
        uint32_t source[4];
        source[0]=own_low;
        w8(set+194u,(value>>1)&1u);
        w8(set+196u,12u);
        w8(set+192u,3u);
        source[3]=0u;
        source[2]=0u;
        source[1]=own_high;
        (void)opencfw_em9305_scan_prepare_3243c0(set+114u,(uintptr_t)source);
        scannable=r8(set+12u);
        response=set+112u;
        w8(set+441u,14u);
    }
    w32(set+420u,CODE(opencfw_em9305_child_31f904));
    w32(set+396u,response);
    if(scannable==1u){
        uintptr_t scan=opencfw_em9305_wsf_event_allocate(0x27u);
        w32(set+400u,scan);
        if(scan==0u){
            opencfw_em9305_wsf_event_release(r32(set+392u));
            w32(set+392u,0u);
            return 0x1fu;
        }
    }
    uint32_t now=opencfw_em9305_scan_current_303f80();
    uint32_t interval=r16(set+10u);
    uint32_t bit=r8(set+16u)==2u?2u:0u;
    uint32_t active=r8(0x8019f8u);
    w32(set+256u,now+1228u);
    w8(set+2u,0u);
    w8(set+1u,0u);
    w32(set+260u,interval*625u);
    uint32_t masks;
    if(active!=0u){
        masks=r8(0x8019fau)&~(1u<<bit);
    }else{
        (void)opencfw_em9305_auxiliary_insert_313220(schedule);
        uint32_t anchor=r32(set+252u);
        uint32_t current=r8(0x8019fau);
        active=r8(0x8019f8u);
        w8(0x8019f9u,bit);
        w32(set+4u,anchor);
        masks=current|(1u<<bit);
    }
    w8(0x8019fau,masks);
    w8(0x8019f8u,active|(1u<<bit));
    return 0u;
}
