#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <sys/mman.h>

extern uint32_t opencfw_em9305_mode_callback_32ca90(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32c86c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cfe8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cb0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cf80(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cf50(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cae4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cde0(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325f0c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325f50(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325dec(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325df4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_326a64(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_326aa8(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32cf94(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3269ec(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_323668(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_31635c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3163ac(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_316594(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32c828(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_326090(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_3260e4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32ce84(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325b98(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32c908(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325b14(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_325a68(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_mode_callback_32c884(uintptr_t,uintptr_t);
static unsigned multiply_calls;
uint32_t opencfw_em9305_test_mpywhl(uint32_t factor,uint32_t period)
{assert(factor==0x30d40u);++multiply_calls;return period==7u?200u:period*10u;}
static unsigned queue_count_calls,whul_calls,w_calls,timing_calls;
static uint32_t test_timing=4u;
uint32_t opencfw_em9305_phy_queue_count_314114(uintptr_t queue)
{assert(queue==0x810168u);++queue_count_calls;return 2u;}
uint32_t opencfw_em9305_ll_event_mode_32d4b0(uintptr_t context)
{assert(context==0x810000u);return 10u;}
uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t length,uint32_t unit)
{assert(length==6u&&unit==10u);++timing_calls;return test_timing;}
uint32_t opencfw_em9305_test_mpywhul(uint32_t a,uint32_t b)
{assert(a==2u&&b==3u);++whul_calls;return 6u;}
uint32_t opencfw_em9305_test_mpyw(uint32_t a,uint32_t b)
{assert(b==3u);++w_calls;return a*b;}
uint32_t opencfw_em9305_pal_current_time(void){return 1000u;}
uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t current,uint32_t previous)
{assert(current==1000u);return current-previous;}
static unsigned value_calls;
uint32_t opencfw_em9305_mode_callback_value_318920(uintptr_t context)
{assert(context==0x810000u);++value_calls;return 0x1234u;}
static unsigned indirect_calls;
static uint32_t indirect_target(uintptr_t context,uintptr_t pointer)
{assert(context==0x810000u&&pointer==(uintptr_t)&indirect_target);++indirect_calls;return 0x4321u;}
static unsigned radio_calls;
uint32_t opencfw_em9305_radio_limit_317b10(uintptr_t context,uintptr_t input)
{assert(context==0x810000u&&(input==0x810236u||input==0x81023eu));++radio_calls;return 0x12345u;}
static unsigned length_calls;
uint32_t opencfw_em9305_phy_length_notify_32317c(uintptr_t context,uint32_t reason)
{assert(context==0x810000u&&reason==0u);++length_calls;return 0x55u;}
static unsigned child_calls;
uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t value)
{assert(value==0x7bu);++child_calls;return 0x12345u;}
static uintptr_t packet_slot;
static unsigned alloc_calls,send_calls,serialize_calls;
static uint32_t alloc_bytes;
static uint32_t serialized_low,serialized_high;
uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t bytes)
{assert(bytes==11u||bytes==9u||bytes==8u||bytes==4u||bytes==2u||bytes==3u||bytes==6u);alloc_bytes=bytes;++alloc_calls;return (uint32_t)packet_slot;}
uint32_t opencfw_em9305_primary_query_313960(uintptr_t output,
                                               uint32_t low,uint32_t high)
{assert(output==0x820001u);++serialize_calls;serialized_low=low;serialized_high=high;return 0x99u;}
uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t context,
                                                  uintptr_t packet)
{assert(context==0x810000u&&packet==0x820000u);++send_calls;return 0x2468u;}
static unsigned reject_calls;
uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t context,uint32_t reason,uint32_t extra)
{assert(context==0x810000u&&((reason==0x24u&&extra==0u)||(reason==30u&&extra==1u)));++reject_calls;return 0xfaceu;}
static unsigned terminate_calls;
uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t context,uint32_t reason)
{assert(context==0x810000u&&(reason==110u||reason==73u));++terminate_calls;return 0x1357u;}
int main(void)
{
    uint8_t *global=mmap((void *)0x802000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *root=mmap((void *)0x805000u,4096u,PROT_READ|PROT_WRITE,
                       MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *context=mmap((void *)0x810000u,4096u,PROT_READ|PROT_WRITE,
                          MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    uint8_t *packet=mmap((void *)0x820000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(global!=(void *)-1&&root!=(void *)-1&&context!=(void *)-1&&packet!=(void *)-1);
    *(uint32_t *)(root+0xc6cu)=0x806000u;
    uint8_t *source=mmap((void *)0x806000u,4096u,PROT_READ|PROT_WRITE,
                         MAP_PRIVATE|MAP_ANONYMOUS|MAP_FIXED,-1,0);
    assert(source!=(void *)-1);
    source[4]=0x5au;
    assert(opencfw_em9305_mode_callback_32ca90((uintptr_t)context,0)==0x810000u);
    assert(context[12]==0x5au);
    *(uint32_t *)(source+4u)=0x12345678u;
    *(uint32_t *)(source+8u)=0x9abcdef0u;
    assert(opencfw_em9305_mode_callback_32c86c((uintptr_t)context,0)==0x810000u);
    assert(*(uint32_t *)(context+712u)==0x9abcdef0u);
    assert(*(uint32_t *)(context+708u)==0x12345678u);
    global[0x81cu]=0xa5u;
    assert(opencfw_em9305_mode_callback_32cfe8((uintptr_t)context,0)==0x810275u);
    assert(context[12]==0xa5u&&context[629]==1u);
    source[4]=0x12u;source[5]=0x34u;
    assert(opencfw_em9305_mode_callback_32cb0c((uintptr_t)context,0)==0x81025eu);
    assert(context[606]==0x12u&&context[607]==0x34u);
    assert(opencfw_em9305_mode_callback_32cf80((uintptr_t)context,0)==0x8102e8u);
    assert(context[744]==0x12u);
    *(uint32_t *)(global+0x81cu)=0xaabbccddu;
    *(uint16_t *)(global+0x820u)=0x1122u;
    assert(opencfw_em9305_mode_callback_32cf50((uintptr_t)context,0)==0x810214u);
    assert(context[526]==1u&&*(uint32_t *)(context+528)==0xaabbccddu);
    assert(*(uint16_t *)(context+532)==0x1122u);
    *(uint32_t *)(global+0x81cu)=0x01020304u;
    assert(opencfw_em9305_mode_callback_32cf50((uintptr_t)context,0)==0x810000u);
    assert(*(uint32_t *)(context+528)==0xaabbccddu);
    *(uint16_t *)(source+4u)=0x6789u;
    *(uint16_t *)(source+6u)=0xabcdu;
    assert(opencfw_em9305_mode_callback_32cae4((uintptr_t)context,0)==0x12345u);
    assert(*(uint16_t *)(context+570u)==0x6789u);
    assert(*(uint16_t *)(context+572u)==0xabcdu);
    assert(*(uint16_t *)(context+590u)==0x2345u&&radio_calls==1u);
    global[0x81cu]=0x7bu;
    context[2]=0u;
    assert(opencfw_em9305_mode_callback_32cde0((uintptr_t)context,0)==0x7bu);
    assert(context[552]==0x7bu&&child_calls==0u);
    context[2]=1u;
    *(uint16_t *)(context+400u)=0xaaaau;
    assert(opencfw_em9305_mode_callback_32cde0((uintptr_t)context,0)==0x12345u);
    assert(context[552]==0x7bu&&*(uint16_t *)(context+200u)==0x2345u);
    assert(*(uint16_t *)(context+400u)==0xaaaau);
    assert(child_calls==1u);
    *(uint32_t *)(root+0xa94u)=0xfedcba98u;
    *(uint32_t *)(root+0xa98u)=0x12345678u;
    packet_slot=(uintptr_t)packet;
    context[2]=0u;
    assert(opencfw_em9305_mode_callback_325f0c((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==8u&&serialized_low==(0xfedcba98u&0xf787cf2fu));
    assert(serialized_high==(0x12345678u&0x1befu));
    context[2]=3u;
    assert(opencfw_em9305_mode_callback_325f0c((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==14u&&send_calls==2u&&serialize_calls==2u);
    *(uint32_t *)(context+544u)=0xa0b0c0d0u;
    assert(opencfw_em9305_mode_callback_325f50((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==9u&&serialized_low==((0xa0b0c0d0u&0xcf2fu)|(0xfedcba98u&0xf7870000u)));
    assert(serialized_high==(0x12345678u&0x1befu));
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_325f0c((uintptr_t)context,0)==0u);
    assert(opencfw_em9305_mode_callback_325f50((uintptr_t)context,0)==0u);
    assert(alloc_calls==5u&&send_calls==3u&&serialize_calls==3u);
    packet_slot=(uintptr_t)packet;
    context[534]=0u;
    context[566]=0x11u;context[567]=0x22u;
    context[570]=0x33u;context[571]=0x44u;
    *(uint16_t *)(context+568)=0xffffu;
    *(uint16_t *)(context+572)=0xffffu;
    assert(opencfw_em9305_mode_callback_325dec((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==0x14u&&packet[1]==0x11u&&packet[2]==0x22u);
    assert(packet[3]==0x48u&&packet[4]==0x08u);
    assert(packet[5]==0x33u&&packet[6]==0x44u);
    assert(packet[7]==0x48u&&packet[8]==0x08u);
    context[534]=1u;context[545]=8u;context[76]=3u;context[77]=3u;
    *(uint16_t *)(context+568)=0u;
    *(uint16_t *)(context+572)=0x100u;
    assert(opencfw_em9305_mode_callback_325df4((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==0x15u&&packet[3]==0x90u&&packet[4]==0x0au);
    assert(packet[7]==0x90u&&packet[8]==0x0au);
    context[76]=0u;context[77]=3u;
    *(uint16_t *)(context+568)=0x100u;
    *(uint16_t *)(context+572)=0x200u;
    assert(opencfw_em9305_mode_callback_325dec((uintptr_t)context,0)==0x2468u);
    assert(packet[3]==0x90u&&packet[4]==0x0au);
    assert(packet[7]==0x00u&&packet[8]==0x02u);
    context[76]=3u;context[77]=0u;
    assert(opencfw_em9305_mode_callback_325df4((uintptr_t)context,0)==0x2468u);
    assert(packet[3]==0x00u&&packet[4]==0x01u);
    assert(packet[7]==0x90u&&packet[8]==0x0au);
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_325dec((uintptr_t)context,0)==0u);
    assert(opencfw_em9305_mode_callback_325df4((uintptr_t)context,0)==0u);
    packet_slot=(uintptr_t)packet;
    context[12]=0x5au;
    assert(opencfw_em9305_mode_callback_326a64((uintptr_t)context,0)==0x2468u);
    assert(alloc_bytes==2u&&packet[0]==2u&&packet[1]==0x5au);
    *(uint32_t *)(root+0xcacu)=0x806000u;
    source[0]=0x10u;source[1]=0x11u;source[2]=0x12u;
    source[3]=0x13u;source[4]=0x14u;
    context[525]=0u;
    assert(opencfw_em9305_mode_callback_326aa8((uintptr_t)context,0)==0x2468u);
    assert(alloc_bytes==6u&&context[525]==1u&&packet[0]==12u);
    assert(packet[1]==0x14u&&packet[2]==0x10u&&packet[3]==0x11u);
    assert(packet[4]==0x12u&&packet[5]==0x13u);
    assert(opencfw_em9305_mode_callback_326aa8((uintptr_t)context,0)==0xfaceu);
    assert(reject_calls==1u);
    context[525]=0u;packet_slot=0u;
    assert(opencfw_em9305_mode_callback_326aa8((uintptr_t)context,0)==0u);
    assert(context[525]==1u&&alloc_bytes==6u);
    global[0x81cu]=5u;global[0x81du]=0x3cu;
    assert(opencfw_em9305_mode_callback_32cf94((uintptr_t)context,0)==0x1357u);
    assert(context[598]==0x3cu&&context[599]==0u&&context[600]==0x3cu);
    assert(terminate_calls==1u);
    packet_slot=(uintptr_t)packet;
    context[606]=0x77u;context[607]=0x88u;
    *(uint32_t *)(context+636u)=0xffffffffu;
    *(uint32_t *)(context+640u)=0x12345678u;
    assert(opencfw_em9305_mode_callback_3269ec((uintptr_t)context,0)==0x1357u);
    assert(alloc_bytes==3u&&packet[0]==25u&&packet[1]==0x77u&&packet[2]==0x88u);
    assert(*(uint32_t *)(context+636u)==0xffffffdfu);
    assert(*(uint32_t *)(context+640u)==0u&&terminate_calls==2u);
    packet_slot=0u;
    *(uint32_t *)(context+636u)=0x21u;
    assert(opencfw_em9305_mode_callback_3269ec((uintptr_t)context,0)==0x1357u);
    assert(*(uint32_t *)(context+636u)==1u&&terminate_calls==3u);
    assert(opencfw_em9305_mode_callback_323668((uintptr_t)context,0)==0x810000u);
    assert(opencfw_em9305_mode_callback_31635c((uintptr_t)context,0)==0x810000u);
    assert(opencfw_em9305_mode_callback_3163ac((uintptr_t)context,0)==0x810000u);
    assert(opencfw_em9305_mode_callback_316594((uintptr_t)context,0)==0x810000u);
    assert((uintptr_t)&indirect_target<=0xffffffffu);
    *(uint32_t *)(root+0x1f4u)=(uint32_t)(uintptr_t)&indirect_target;
    *(uint32_t *)(root+0x2c4u)=(uint32_t)(uintptr_t)&indirect_target;
    *(uint32_t *)(root+0x6d8u)=(uint32_t)(uintptr_t)&indirect_target;
    assert(opencfw_em9305_mode_callback_31635c((uintptr_t)context,0)==0x4321u);
    assert(opencfw_em9305_mode_callback_3163ac((uintptr_t)context,0)==0x4321u);
    assert(opencfw_em9305_mode_callback_316594((uintptr_t)context,0)==0x4321u);
    assert(indirect_calls==3u);
    *(uint16_t *)(context+262u)=0x0100u;
    *(uint32_t *)(global+0x81cu)=0x11111111u;
    *(uint32_t *)(global+0x820u)=0x22222222u;
    *(uint32_t *)(global+0x824u)=0x0120u;
    assert(opencfw_em9305_mode_callback_32c828((uintptr_t)context,0)==0x810000u);
    assert(*(uint32_t *)(context+708u)==0x11111111u);
    assert(*(uint32_t *)(context+712u)==0x22222222u);
    assert(*(uint32_t *)(context+716u)==0x0120u);
    *(uint32_t *)(global+0x824u)=0x8100u;
    assert(opencfw_em9305_mode_callback_32c828((uintptr_t)context,0)==0x1357u);
    root[0xaa8u]=0x80u; /* signed -128 */
    packet_slot=(uintptr_t)packet;
    context[744]=1u;context[746]=0x7fu;
    assert(opencfw_em9305_mode_callback_326090((uintptr_t)context,0)==0x2468u);
    assert(context[746]==0x80u&&packet[0]==29u&&packet[1]==0x34u);
    context[744]=0u;context[746]=0x81u;
    assert(opencfw_em9305_mode_callback_326090((uintptr_t)context,0)==0x2468u);
    assert(context[746]==0x81u); /* -127 is not below -128 */
    root[0xaa8u]=0x7fu;
    assert(opencfw_em9305_mode_callback_326090((uintptr_t)context,0)==0x2468u);
    assert(context[746]==0x7fu);
    context[744]=2u;context[746]=0x33u;
    assert(opencfw_em9305_mode_callback_326090((uintptr_t)context,0)==0x2468u);
    assert(context[746]==0x33u);
    assert(opencfw_em9305_mode_callback_3260e4((uintptr_t)context,0)==0x2468u);
    assert(packet[0]==30u&&packet[1]==0x34u&&value_calls==5u);
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_326090((uintptr_t)context,0)==0u);
    assert(opencfw_em9305_mode_callback_3260e4((uintptr_t)context,0)==0u);
    assert(value_calls==5u);
    *(uint16_t *)(global+0x820u)=26u;
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==0x810000u);
    *(uint16_t *)(global+0x820u)=100u;
    *(uint16_t *)(global+0x81cu)=26u;
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==0x810000u);
    *(uint16_t *)(global+0x81cu)=100u;
    *(uint16_t *)(global+0x822u)=328u;
    *(uint16_t *)(global+0x81eu)=100u;
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==328u);
    *(uint16_t *)(global+0x81eu)=328u;
    *(uint16_t *)(global+0x822u)=100u;
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==100u);
    *(uint16_t *)(global+0x822u)=328u;
    context[534]=1u;context[545]=8u;context[76]=0u;context[77]=0u;
    *(uint16_t *)(context+566u)=120u;
    *(uint16_t *)(context+568u)=120u;
    *(uint16_t *)(context+570u)=120u;
    *(uint16_t *)(context+572u)=120u;
    *(uint16_t *)(context+574u)=0u;
    *(uint16_t *)(context+576u)=0u;
    *(uint16_t *)(context+578u)=0u;
    *(uint16_t *)(context+580u)=0u;
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==0x12345u);
    assert(length_calls==1u&&*(uint16_t *)(context+592u)==0x2345u);
    assert(*(uint16_t *)(context+580u)==120u);
    assert(*(uint16_t *)(context+576u)==120u);
    assert(*(uint16_t *)(context+578u)==100u);
    assert(*(uint16_t *)(context+574u)==100u);
    assert(opencfw_em9305_mode_callback_32ce84((uintptr_t)context,0)==0x12345u);
    assert(length_calls==1u);
    packet_slot=(uintptr_t)packet;
    for (unsigned i=0;i<9u;++i) {
        source[4u+4u*i]=1u;source[5u+4u*i]=2u;
        source[6u+4u*i]=3u;source[7u+4u*i]=0u;
    }
    source[40]=0x5eu;
    *(uint32_t *)(context+636u)=0xffffffffu;
    *(uint32_t *)(context+640u)=0x12345678u;
    assert(opencfw_em9305_mode_callback_325b98((uintptr_t)context,0)==0x1357u);
    assert(alloc_bytes==11u&&packet[0]==0x29u&&packet[10]==0x5eu);
    for (unsigned i=1;i<=9u;++i) assert(packet[i]==0x39u);
    assert(*(uint32_t *)(context+636u)==0xfffffdffu);
    assert(*(uint32_t *)(context+640u)==0u);
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_325b98((uintptr_t)context,0)==0x1357u);
    context[2]=1u;
    assert(opencfw_em9305_mode_callback_32c908((uintptr_t)context,0)==0x1357u);
    context[2]=0u;context[565]=0u;
    assert(opencfw_em9305_mode_callback_32c908((uintptr_t)context,0)==0x1357u);
    context[565]=1u;
    *(uint32_t *)(context+928u)=0xdeadbeefu;
    *(uint32_t *)(context+944u)=0x12345678u;
    *(uint32_t *)(context+232u)=900u;
    *(uint32_t *)(context+236u)=101u;
    assert(opencfw_em9305_mode_callback_32c908((uintptr_t)context,0)==100u);
    *(uint32_t *)(context+236u)=100u;
    for (unsigned i=0;i<9u;++i) global[0x81cu+i]=0xffu;
    global[0x825u]=0x6du;
    assert(opencfw_em9305_mode_callback_32c908((uintptr_t)context,0)==1u);
    for (unsigned i=0;i<9u;++i) {
        assert(context[193u+4u*i]==3u);
        assert(context[194u+4u*i]==0x0cu);
        assert(context[195u+4u*i]==0x30u);
        assert(context[196u+4u*i]==0xc0u);
    }
    assert(context[229u]==1u);
    assert(*(uint32_t *)(context+928u)==0xdeadbeefu);
    assert(*(uint32_t *)(context+944u)==0x12345678u);
    context[2]=1u;
    *(uint32_t *)(context+636u)=0xffffffffu;
    *(uint32_t *)(context+640u)=0x1234u;
    assert(opencfw_em9305_mode_callback_325b14((uintptr_t)context,0)==0x1357u);
    assert(*(uint32_t *)(context+636u)==0xfffffeffu);
    assert(*(uint32_t *)(context+640u)==0u&&multiply_calls==0u);
    context[2]=0u;packet_slot=(uintptr_t)packet;
    *(uint32_t *)(root+0xc6cu)=0x806000u;
    source[4]=1u;source[5]=7u;source[6]=0x55u;
    assert(opencfw_em9305_mode_callback_325b14((uintptr_t)context,0)==0x1357u);
    assert(alloc_bytes==4u&&packet[0]==0x28u&&packet[1]==1u);
    assert(packet[2]==7u&&packet[3]==0x55u);
    assert(context[565]==1u&&*(uint32_t *)(context+236u)==200u);
    assert(*(uint32_t *)(context+232u)==800u&&multiply_calls==1u);
    assert(*(uint32_t *)(context+928u)==0xdeadbeefu);
    assert(*(uint32_t *)(context+944u)==0x12345678u);
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_325b14((uintptr_t)context,0)==0x1357u);
    assert(multiply_calls==2u);
    packet_slot=(uintptr_t)packet;
    *(uint32_t *)(root+0xcacu)=0x806000u;
    *(uint16_t *)(source+38u)=3u;
    *(uint16_t *)(context+262u)=100u;
    *(uint16_t *)(context+260u)=2u;
    *(uint16_t *)(context+846u)=3u;
    context[708]=0x11u;context[709]=0x22u;context[710]=0x33u;
    context[711]=0x44u;context[712]=0x55u;
    assert(opencfw_em9305_mode_callback_325a68((uintptr_t)context,0)==0x2468u);
    assert(alloc_bytes==8u&&packet[0]==1u&&packet[1]==0x11u);
    assert(packet[2]==0x22u&&packet[3]==0x33u&&packet[4]==0x44u);
    assert(packet[5]==0x55u&&packet[6]==0x9au&&packet[7]==0u);
    assert(queue_count_calls==1u&&whul_calls==1u&&timing_calls==1u&&w_calls==1u);
    test_timing=7u;
    assert(opencfw_em9305_mode_callback_325a68((uintptr_t)context,0)==0x2468u);
    assert(queue_count_calls==3u&&whul_calls==3u&&timing_calls==3u&&w_calls==2u);
    packet_slot=0u;
    assert(opencfw_em9305_mode_callback_325a68((uintptr_t)context,0)==0u);
    context[2]=0u;
    *(uint32_t *)(context+636u)=0xffffffffu;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==0x1357u);
    assert(*(uint32_t *)(context+636u)==0xfffffeffu);
    context[2]=1u;
    global[0x81cu]=2u;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==0xfaceu);
    global[0x81cu]=0u;global[0x81du]=4u;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==0xfaceu);
    global[0x81du]=10u;global[0x81eu]=9u;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==0xfaceu);
    global[0x81eu]=20u;
    *(uint32_t *)(context+240u)=0xfeedbeefu;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==1000u);
    assert(context[565]==0u&&*(uint32_t *)(context+236u)==200u);
    assert(*(uint32_t *)(context+232u)==100u);
    assert(*(uint32_t *)(context+240u)==0xfeedbeefu);
    assert(*(uint32_t *)(context+228u)==1000u);
    global[0x81cu]=1u;
    assert(opencfw_em9305_mode_callback_32c884((uintptr_t)context,0)==1000u);
    assert(context[565]==1u&&*(uint32_t *)(context+240u)==1000u);
    *(uint32_t *)(global+0x824u)=0x0120u;
    *(uint32_t *)(global+0x81cu)=0u;
    *(uint32_t *)(global+0x820u)=0u;
    assert(opencfw_em9305_mode_callback_32c828((uintptr_t)context,0)==0x1357u);
    return 0;
}
