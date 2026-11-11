#include <stdint.h>

/* Native 0x320088..0x320274: initialise the advertising set record for a
 * connectable start: clear the 240-byte block at +244, install the
 * scheduler callbacks (320274, 320dd8, 320e00, 31fb98) and defaults
 * (first channel from 325708, access address 0x8e89bed6, CRC init
 * 0x555555, 0x83 / 512 / 0x02830283 windows by PHY mode +98, header flags
 * +372 with the coded bit), allocate the 66-byte PDU buffer (+392; 0x1f when
 * none), take a random access address, CRC seed, the connection timing
 * (0x805aa0/0x805aa4, +90, params +4/+6), random hop and clock accuracy,
 * the own address (static 0x805b40 or public 0x805a8c by bit 0 of +99,
 * with resolution flags 0x51 when 0x805a9d is set) and, for PHY mode 0,
 * the peer address and type; then encode the advertising header (+112
 * from +192) and payload. Returns 0. */
extern void *opencfw_em9305_memset(void *dst,uint32_t value,uint32_t count);
extern void opencfw_em9305_child_320274(uintptr_t context);
extern uint32_t opencfw_em9305_init_channel_first_325708(uint32_t flags);
extern uint32_t opencfw_em9305_child_320dd8(uintptr_t record,uintptr_t command);
extern void opencfw_em9305_child_320e00(uintptr_t owner,uintptr_t pdu);
extern uintptr_t opencfw_em9305_wsf_event_allocate(uint32_t length);
extern uint32_t opencfw_em9305_child_31fb98(uint32_t a);
extern uint32_t opencfw_em9305_radio_access_raw_318878(void);
extern uint32_t opencfw_em9305_radio_crc_seed_318960(void);
extern uint32_t opencfw_em9305_associated_random_31896c(void);
extern uint32_t opencfw_em9305_compose_accuracy_318988(void);
extern uint32_t opencfw_em9305_radio_encode_3239d4(uintptr_t output,
                                                   uintptr_t input);
extern uint32_t opencfw_em9305_radio_encode_323c94(uintptr_t output,
                                                   uintptr_t input);

static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
#define CODE(f) ((uint32_t)(uintptr_t)(f))

uint32_t opencfw_em9305_child_320088(uintptr_t set,uintptr_t params,
                                     uint32_t peer_low,uint32_t peer_high,
                                     uint32_t peer_type)
{
    (void)opencfw_em9305_memset((void *)(set+244u),0u,240u);
    w32(set+288u,set+292u);
    uint32_t channels=r8(0x805b00u);
    w8(set+270u,1u);
    w8(set+268u,3u);
    w8(set+292u,2u);
    w32(set+272u,CODE(opencfw_em9305_child_320274));
    w32(set+280u,set);
    w32(set+276u,CODE(opencfw_em9305_child_320274));
    uint32_t first=opencfw_em9305_init_channel_first_325708(channels);
    uint32_t role=r8(set+16u);
    uint32_t mode=r8(set+98u);
    w8(set+293u,first);
    w32(set+300u,0x555555u);
    w32(set+296u,0x8e89bed6u);
    uint32_t accuracy=r8(0x805a9cu);
    uint32_t kind=((role==2u)?2u:0u)+1u;
    w16(set+368u,0x83u);
    w8(set+294u,accuracy);
    w8(set+305u,kind);
    w8(set+304u,kind);
    if(mode==4u||mode==1u)w16(set+370u,0x83u);
    else if(mode==2u)w16(set+368u,512u);
    else if(mode==3u)w32(set+368u,0x02830283u);
    uint32_t flags=(r32(set+372u)&~0x80u)|((mode==4u?1u:0u)<<7);
    channels=r8(0x805b00u);
    w32(set+372u,flags);
    w32(set+412u,CODE(opencfw_em9305_child_320e00));
    w32(set+408u,CODE(opencfw_em9305_child_320dd8));
    w8(set+442u,0x42u);
    w8(set+443u,channels);
    uintptr_t buffer=opencfw_em9305_wsf_event_allocate(0x42u);
    w32(set+392u,buffer);
    if(buffer==0u)return 0x1fu;
    w32(set+416u,CODE(opencfw_em9305_child_31fb98));
    uint32_t access=opencfw_em9305_radio_access_raw_318878();
    w32(set+52u,access);
    uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
    uint32_t timing_high=r32(0x805aa4u),timing_low=r32(0x805aa0u);
    uint32_t interval=r16(set+90u);
    uint32_t latency=r16(params+4u),timeout=r16(params+6u);
    w8(set+74u,1u);
    w32(set+56u,crc);
    w32(set+64u,timing_high);
    w32(set+60u,timing_low);
    w16(set+68u,interval);
    w16(set+70u,latency);
    w16(set+72u,timeout);
    uint32_t hop=opencfw_em9305_associated_random_31896c();
    w8(set+78u,hop);
    uint32_t sca=opencfw_em9305_compose_accuracy_318988();
    uint32_t options=r8(set+99u);
    uint32_t header=r32(set+372u);
    w8(set+192u,5u);
    w8(set+196u,0x22u);
    w8(set+79u,sca);
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
    uint32_t direct=r8(set+98u);
    w32(set+36u,own_low);
    w32(set+40u,own_high);
    w8(set+194u,(value>>1)&1u);
    if(direct==0u){
        uint32_t type=peer_type&1u;
        w8(set+195u,type);
        w32(set+384u,peer_low);
        w32(set+44u,peer_low);
        w32(set+388u,peer_high);
        w32(set+48u,peer_high);
        w32(set+372u,(type<<3)|value|4u);
    }
    uint32_t used=opencfw_em9305_radio_encode_3239d4(set+112u,set+192u);
    (void)opencfw_em9305_radio_encode_323c94(used+set+112u,set+36u);
    w32(set+396u,set+112u);
    w8(set+441u,0x24u);
    return 0u;
}
