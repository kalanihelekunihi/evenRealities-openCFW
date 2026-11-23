#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x3263ec..0x3266ce: complete second connection packet constructor.
 * The ARC DSP operations are written as C arithmetic. Resident radio
 * effects remain in the selected child providers. */
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_compose_accuracy_318988(void);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);

static uint32_t native_mpywhl(uint32_t left,uint32_t right)
{
return (uint32_t)left*(uint32_t)(int32_t)(int16_t)right;
}
static uint32_t native_mpywhul(uint32_t left,uint32_t right)
{
return (uint32_t)left*(uint16_t)right;
}
struct native_mac_div_result {uint32_t quotient,low;};
/* Native 3264c4 MOV R58 precedes the volatile period load at 3264ca.
 * DIVU R1 destination starts as the state address, not the scheduled time;
 * that would only show for a zero denominator with STATUS32.DZ clear.
 * A zero divisor traps: stock sets STATUS32.DZ at startup (0x302b1a) and the
 * EV_DivZero handler 0x30f170 resets the chip; C division emits the same DIVU.
 * MetaWare scheduled the accumulator load before the DIVU, so DIVU does not
 * disturb ACC0 on this core. */
static struct native_mac_div_result native_divu_macwhul_from_state(
    uint32_t numerator,uintptr_t period_address,uint32_t scheduled,uint32_t state_address)
{
    uint32_t period=*(volatile uint32_t *)period_address;
    (void)state_address;
    uint32_t quotient=numerator/period;
    struct native_mac_div_result result={quotient,scheduled+(uint32_t)((uint64_t)period*(uint16_t)(quotient+1u))};
    return result;
}
/* prior: register stock DIVU leaves only for a zero divisor with DZ clear. */
static uint32_t native_divu_prior(uint32_t numerator,uint32_t denominator,uint32_t prior)
{
(void)prior;return numerator/denominator;
}
static uint32_t native_mpymu(uint32_t left,uint32_t right)
{
return (uint32_t)(((uint64_t)left*(uint32_t)right)>>32);
}
struct product_pair {uint32_t low,high;};
static struct product_pair native_mpydu(uint32_t left,uint32_t right)
{
uint64_t product=(uint64_t)left*right;struct product_pair p={(uint32_t)product,(uint32_t)(product>>32u)};return p;
}

uint32_t opencfw_em9305_init_registered_3263ec(uintptr_t root)
{
    uint32_t slot=*(volatile uint16_t *)(root+612u);
    uint32_t slot_offset=(uint32_t)(uint16_t)slot*784u;
    uintptr_t state=((uintptr_t)&em9305_ram_803d58 + 0x84u)+slot_offset;
    uintptr_t product=((uintptr_t)&em9305_ram_803d58 + 0x328u)+slot_offset;
    uint32_t custom=*(volatile uint8_t *)(product+1u);
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(35u+(custom!=0u?8u:0u));
    if(packet==0u)return 0u;
    uint32_t root_half=*(volatile uint16_t *)(root+260u);
    uint32_t scheduled=*(volatile uint32_t *)(state+172u);
    uint32_t count=*(volatile uint16_t *)(state+176u);
    custom=*(volatile uint8_t *)(product+1u);
    uint32_t initial_step=root_half+7u;
    if(custom!=0u) {
        uintptr_t product_ptr=*(volatile uint32_t *)(product+4u);
        uint32_t slots=*(volatile uint8_t *)(product_ptr+18u);
        if((slots&127u)==0u) {
            slots=*(volatile uint8_t *)(uintptr_t)(((uintptr_t)&em9305_ram_803d58 + 0x220u)+slot_offset);
            if(slots<2u)goto no_custom_step;
        }
        uint32_t stride_product=slots*(uint32_t)-1250;
        uint32_t timing=*(volatile uint8_t *)(uintptr_t)(((uintptr_t)&em9305_ram_803d58 + 0x221u)+slot_offset);
        uint32_t period=*(volatile uint32_t *)(state+152u);
        ++count;
        scheduled=period+scheduled+native_mpywhl(stride_product+1250u,timing);
    }
no_custom_step:
    uint32_t half=*(volatile uint16_t *)(root+262u);
    uint32_t first_time=opencfw_em9305_init_secondary_schedule_318ad8(
        root,(uint16_t)(half+initial_step));
    uint32_t guard_operand=*(volatile uint16_t *)(root+592u);
    uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
    uint32_t gap=opencfw_em9305_auxiliary_elapsed_303f8c(
        guard+(first_time+guard_operand),scheduled);
    if(gap!=0u) {
        uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(gap,scheduled);
        struct native_mac_div_result update=native_divu_macwhul_from_state(
            elapsed,state+152u,scheduled,(uint32_t)state);
        count+=update.quotient+1u;
        scheduled=update.low;
    } else {
        uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(scheduled,gap);
        uint32_t period=*(volatile uint32_t *)(state+152u);
        uint32_t quotient=native_divu_prior(elapsed,period,elapsed);
        uint32_t produced=native_mpywhul(period,quotient);
        count-=quotient;
        scheduled-=produced;
    }
    uint32_t quantized_elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(scheduled,first_time);
    uint32_t selector,overflow,quantized;
    if(quantized_elapsed<0x3bfc4u) {
        quantized=native_mpymu(quantized_elapsed,0x11111112u)>>1u;
        selector=0u;overflow=0u;
    } else {
        selector=1u;
        overflow=quantized_elapsed>0x257fffu;
        if(overflow!=0u)quantized_elapsed-=0x258000u;
        uint32_t high=native_mpymu(quantized_elapsed,0x69d0369eu);
        quantized=(high+3u*quantized_elapsed)>>10u;
    }
    custom=*(volatile uint8_t *)(product+1u);
    *(volatile uint8_t *)(packet+0u)=(uint8_t)(custom!=0u?0x2au:0x1cu);
    uint32_t packet_byte1=*(volatile uint8_t *)(root+610u);
    *(volatile uint8_t *)(packet+1u)=(uint8_t)packet_byte1;
    uint32_t packet_byte2=*(volatile uint8_t *)(root+611u);
    *(volatile uint8_t *)(packet+4u)=(uint8_t)((quantized|(selector<<13u)|(overflow<<14u))>>8u);
    *(volatile uint8_t *)(packet+3u)=(uint8_t)quantized;
    *(volatile uint8_t *)(packet+2u)=(uint8_t)packet_byte2;
    uint32_t period=*(volatile uint32_t *)(state+152u);
    struct product_pair pair=native_mpydu(period,0x1a36e3u);
    *(volatile uint8_t *)(packet+5u)=(uint8_t)((pair.high<<1u)|(pair.low>>31u));
    period=*(volatile uint32_t *)(state+152u);
    *(volatile uint8_t *)(packet+6u)=(uint8_t)(native_mpymu(period,0x1a36e3u)>>7u);
    uint32_t accuracy_seed=*(volatile uint8_t *)(state+156u);
    uint32_t low=*(volatile uint32_t *)(state+544u);
    uint32_t high=*(volatile uint32_t *)(state+548u);
    *(volatile uint8_t *)(packet+7u)=(uint8_t)low;
    *(volatile uint8_t *)(packet+10u)=(uint8_t)(low>>24u);
    *(volatile uint8_t *)(packet+9u)=(uint8_t)(low>>16u);
    *(volatile uint8_t *)(packet+8u)=(uint8_t)(low>>8u);
    *(volatile uint8_t *)(packet+11u)=(uint8_t)((accuracy_seed<<5u)|high);
    uint32_t word=*(volatile uint32_t *)(state+0u);
    *(volatile uint8_t *)(packet+12u)=(uint8_t)word;
    word=*(volatile uint32_t *)(state+0u);
    *(volatile uint8_t *)(packet+13u)=(uint8_t)(word>>8u);
    *(volatile uint8_t *)(packet+14u)=(uint8_t)*(volatile uint16_t *)(state+2u);
    *(volatile uint8_t *)(packet+15u)=*(volatile uint8_t *)(state+3u);
    word=*(volatile uint32_t *)(state+4u);
    *(volatile uint8_t *)(packet+16u)=(uint8_t)word;
    word=*(volatile uint32_t *)(state+4u);
    *(volatile uint8_t *)(packet+17u)=(uint8_t)(word>>8u);
    uint32_t packet_byte18=*(volatile uint16_t *)(state+6u);
    *(volatile uint8_t *)(packet+20u)=(uint8_t)(count>>8u);
    *(volatile uint8_t *)(packet+19u)=(uint8_t)count;
    *(volatile uint8_t *)(packet+18u)=(uint8_t)packet_byte18;
    half=*(volatile uint16_t *)(root+262u);
    *(volatile uint8_t *)(packet+21u)=(uint8_t)(root_half+half+7u);
    half=*(volatile uint16_t *)(root+262u);
    *(volatile uint8_t *)(packet+22u)=(uint8_t)((half+(uint16_t)initial_step)>>8u);
    *(volatile uint8_t *)(packet+23u)=*(volatile uint8_t *)(state+176u);
    *(volatile uint8_t *)(packet+24u)=*(volatile uint8_t *)(state+177u);
    uint32_t upper=*(volatile uint8_t *)(state+618u);
    uint32_t lower=*(volatile uint8_t *)(state+616u);
    uint32_t accuracy=opencfw_em9305_compose_accuracy_318988();
    *(volatile uint8_t *)(packet+25u)=(uint8_t)((upper<<4u)|lower|(accuracy<<5u));
    uint32_t mode=*(volatile uint8_t *)(state+676u);
    uint32_t mapped=mode-2u;
    *(volatile uint8_t *)(packet+26u)=(uint8_t)(mapped<3u?(0x80402u>>(mapped*8u)):1u);
    uint32_t address_high=*(volatile uint32_t *)(state+632u);
    uint32_t address_low=*(volatile uint32_t *)(state+628u);
    (void)opencfw_em9305_radio_address_write_3045e8(packet+27u,address_low,address_high);
    *(volatile uint8_t *)(packet+33u)=*(volatile uint8_t *)(root+262u);
    *(volatile uint8_t *)(packet+34u)=*(volatile uint8_t *)(root+263u);
    custom=*(volatile uint8_t *)(product+1u);
    if(custom!=0u) {
        word=*(volatile uint32_t *)(state+408u);
        *(volatile uint8_t *)(packet+35u)=(uint8_t)word;
        word=*(volatile uint32_t *)(state+408u);
        *(volatile uint8_t *)(packet+36u)=(uint8_t)(word>>8u);
        *(volatile uint8_t *)(packet+37u)=(uint8_t)*(volatile uint16_t *)(state+410u);
        *(volatile uint8_t *)(packet+38u)=*(volatile uint8_t *)(state+411u);
        *(volatile uint8_t *)(packet+39u)=*(volatile uint8_t *)(state+412u);
        *(volatile uint8_t *)(packet+40u)=*(volatile uint8_t *)(state+413u);
        *(volatile uint8_t *)(packet+41u)=*(volatile uint8_t *)(state+414u);
        *(volatile uint8_t *)(packet+42u)=*(volatile uint8_t *)(state+415u);
    }
    return opencfw_em9305_phy_packet_send_32d32c(root,packet);
}
