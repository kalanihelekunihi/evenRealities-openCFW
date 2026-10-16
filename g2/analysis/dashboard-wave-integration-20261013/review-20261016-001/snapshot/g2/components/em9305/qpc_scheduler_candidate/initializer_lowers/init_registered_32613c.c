#include <stdint.h>

/* Native 0x32613c..0x3263ea: complete first connection packet constructor.
 * The ARC DSP operations are preserved as named instructions. Resident radio
 * effects remain in the selected child providers. */
extern uintptr_t opencfw_em9305_radio_record_find_31aa64(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_alloc_32d2f0(uint32_t);
extern uint32_t opencfw_em9305_phy_packet_send_32d32c(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_guard_interval(void);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_compose_accuracy_318988(void);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);

static uint32_t native_mpywhl(uint32_t left,uint32_t right)
{
#ifdef __arc__
uint32_t result;__asm__ volatile("mpywhl %0,%1,%2":"=r"(result):"r"(left),"r"(right):"r58","r59","memory");return result;
#else
return (uint32_t)((int64_t)(int32_t)left*(int16_t)right);
#endif
}
static uint32_t native_mpywhul(uint32_t left,uint32_t right)
{
#ifdef __arc__
uint32_t result;__asm__ volatile("mpywhul %0,%1,%2":"=r"(result):"r"(left),"r"(right):"r58","r59","memory");return result;
#else
return (uint32_t)((uint64_t)left*(uint16_t)right);
#endif
}
struct native_mac_div_result {uint32_t quotient,low;};
/* Preserve the stock MOV R58 -> DIVU -> MACWHUL instruction order. On a
 * radix-2 DSP divider DIVU may update ACC0_LO, so moving R58 after division
 * would change the native low-word result. The host fallback models the
 * non-radix-2 case only; hardware selection remains an explicit gate. */
static struct native_mac_div_result native_divu_macwhul(
    uint32_t numerator,uint32_t denominator,uint32_t prior)
{
#ifdef __arc__
    uint32_t quotient=prior,iteration,low;
    __asm__ volatile("mov r58,%3\n\tdivu %0,%4,%5\n\tadd %1,%0,1\n\tmacwhul %2,%5,%1"
        : "+&r"(quotient),"=&r"(iteration),"=&r"(low)
        : "r"(prior),"r"(numerator),"r"(denominator)
        : "r58","r59","memory");
    struct native_mac_div_result result={quotient,low};return result;
#else
    uint32_t quotient=denominator==0u?prior:numerator/denominator;
    struct native_mac_div_result result={quotient,prior+(uint32_t)((uint64_t)denominator*(uint16_t)(quotient+1u))};
    return result;
#endif
}
static uint32_t native_divu_prior(uint32_t numerator,uint32_t denominator,uint32_t prior)
{
#ifdef __arc__
__asm__ volatile("divu %0,%1,%2":"+r"(prior):"r"(numerator),"r"(denominator):"memory");return prior;
#else
return denominator==0u?prior:numerator/denominator;
#endif
}
static uint32_t native_mpymu(uint32_t left,uint32_t right)
{
#ifdef __arc__
uint32_t result;__asm__ volatile("mpymu %0,%1,%2":"=r"(result):"r"(left),"r"(right):"r58","r59","memory");return result;
#else
return (uint32_t)(((uint64_t)left*right)>>32u);
#endif
}
struct product_pair {uint32_t low,high;};
static struct product_pair native_mpydu(uint32_t left,uint32_t right)
{
#ifdef __arc__
register uint32_t low __asm__("r4"),high __asm__("r5");__asm__ volatile("mpydu r4,%2,%3":"=r"(low),"=r"(high):"r"(left),"r"(right):"r58","r59","memory");struct product_pair p={low,high};return p;
#else
uint64_t product=(uint64_t)left*right;struct product_pair p={(uint32_t)product,(uint32_t)(product>>32u)};return p;
#endif
}

uint32_t opencfw_em9305_init_registered_32613c(uintptr_t root)
{
    uint32_t id=*(volatile uint8_t *)(root+612u);
    uintptr_t record=opencfw_em9305_radio_record_find_31aa64(id);
    uintptr_t custom_slot=record+2809u;
    uint32_t custom=*(volatile uint8_t *)custom_slot;
    uintptr_t packet=opencfw_em9305_phy_packet_alloc_32d2f0(35u+(custom!=0u?8u:0u));
    if(packet==0u)return 0u;
    uint32_t native_r25=*(volatile uint16_t *)(root+260u);
    custom=*(volatile uint8_t *)custom_slot;
    uint32_t scheduled=*(volatile uint32_t *)(record+388u);
    uint32_t counter=*(volatile uint16_t *)(record+376u);
    uint32_t native_r19=native_r25+7u;
    if(custom!=0u) {
        uint32_t slots=*(volatile uint8_t *)(record+799u);
        if((slots&127u)!=0u) {
            uint32_t stride=*(volatile uint32_t *)(record+792u);
            uint32_t period=*(volatile uint32_t *)(record+700u);
            ++counter;
            scheduled=period+scheduled-native_mpywhl(stride,slots);
        }
    }
    uint32_t half=*(volatile uint16_t *)(root+262u);
    uint32_t first_time=opencfw_em9305_init_secondary_schedule_318ad8(
        root,(uint16_t)(half+native_r19));
    uint32_t guard_operand=*(volatile uint16_t *)(root+592u);
    uint32_t guard=opencfw_em9305_auxiliary_guard_interval();
    uint32_t gap=opencfw_em9305_auxiliary_elapsed_303f8c(
        guard+(first_time+guard_operand),scheduled);
    if(gap!=0u) {
        uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(gap,scheduled);
        uint32_t period=*(volatile uint32_t *)(record+700u);
        struct native_mac_div_result update=native_divu_macwhul(elapsed,period,scheduled);
        counter=update.quotient+counter+1u;
        scheduled=update.low;
    } else {
        uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(scheduled,gap);
        uint32_t period=*(volatile uint32_t *)(record+700u);
        uint32_t quotient=native_divu_prior(elapsed,period,elapsed);
        uint32_t produced=native_mpywhul(period,quotient);
        counter-=quotient;
        scheduled-=produced;
    }
    uint32_t quantized_elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(
        scheduled,first_time);
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
    custom=*(volatile uint8_t *)custom_slot;
    *(volatile uint8_t *)(packet+0u)=(uint8_t)(custom!=0u?0x2au:0x1cu);
    *(volatile uint8_t *)(packet+1u)=*(volatile uint8_t *)(root+610u);
    uint32_t packet_byte2=*(volatile uint8_t *)(root+611u);
    *(volatile uint8_t *)(packet+4u)=(uint8_t)((quantized|(selector<<13u)|(overflow<<14u))>>8u);
    *(volatile uint8_t *)(packet+3u)=(uint8_t)quantized;
    *(volatile uint8_t *)(packet+2u)=(uint8_t)packet_byte2;
    uint32_t period=*(volatile uint32_t *)(record+700u);
    struct product_pair product=native_mpydu(period,0x1a36e3u);
    *(volatile uint8_t *)(packet+5u)=(uint8_t)((product.high<<1u)|(product.low>>31u));
    period=*(volatile uint32_t *)(record+700u);
    *(volatile uint8_t *)(packet+6u)=(uint8_t)(native_mpymu(period,0x1a36e3u)>>7u);
    uint32_t low=*(volatile uint32_t *)(record+720u);
    uint32_t high=*(volatile uint32_t *)(record+724u);
    uint32_t accuracy=opencfw_em9305_compose_accuracy_318988();
    *(volatile uint8_t *)(packet+10u)=(uint8_t)(low>>24u);
    *(volatile uint8_t *)(packet+7u)=(uint8_t)low;
    *(volatile uint8_t *)(packet+9u)=(uint8_t)(low>>16u);
    *(volatile uint8_t *)(packet+8u)=(uint8_t)(low>>8u);
    *(volatile uint8_t *)(packet+11u)=(uint8_t)((accuracy<<5u)|high);
    uint32_t word=*(volatile uint32_t *)(record+432u);
    *(volatile uint8_t *)(packet+12u)=(uint8_t)word;
    word=*(volatile uint32_t *)(record+432u);
    *(volatile uint8_t *)(packet+13u)=(uint8_t)(word>>8u);
    *(volatile uint8_t *)(packet+14u)=(uint8_t)*(volatile uint16_t *)(record+434u);
    *(volatile uint8_t *)(packet+15u)=*(volatile uint8_t *)(record+435u);
    word=*(volatile uint32_t *)(record+436u);
    *(volatile uint8_t *)(packet+16u)=(uint8_t)word;
    word=*(volatile uint32_t *)(record+436u);
    *(volatile uint8_t *)(packet+17u)=(uint8_t)(word>>8u);
    uint32_t packet_byte18=*(volatile uint16_t *)(record+438u);
    *(volatile uint8_t *)(packet+19u)=(uint8_t)counter;
    *(volatile uint8_t *)(packet+20u)=(uint8_t)(counter>>8u);
    *(volatile uint8_t *)(packet+18u)=(uint8_t)packet_byte18;
    half=*(volatile uint16_t *)(root+262u);
    *(volatile uint8_t *)(packet+21u)=(uint8_t)(half+native_r25+7u);
    half=*(volatile uint16_t *)(root+262u);
    *(volatile uint8_t *)(packet+22u)=(uint8_t)((half+(uint16_t)native_r19)>>8u);
    *(volatile uint8_t *)(packet+23u)=*(volatile uint8_t *)(record+376u);
    *(volatile uint8_t *)(packet+24u)=*(volatile uint8_t *)(record+377u);
    uint32_t mode=*(volatile uint8_t *)(record+57u);
    uint32_t flag=0u;
    if((mode&1u)!=0u) {
        flag=16u;
        if(*(volatile uint8_t *)(record+4u)!=0u)goto flag_ready;
    }
    flag=0u;
    if(mode==2u) {
        uint32_t bits=*(volatile uint32_t *)(record+20u)&0xc000u;
#ifdef __arc__
        __asm__ volatile("bxor.f 0,%1,14\n\tmov.eq %0,16":"+r"(flag):"r"(bits):"cc","memory");
#else
        if(bits==0x4000u)flag=16u;
#endif
    }
flag_ready:
    uint32_t channel=*(volatile uint8_t *)(record+66u);
    accuracy=opencfw_em9305_compose_accuracy_318988();
    *(volatile uint8_t *)(packet+25u)=(uint8_t)((flag|channel)|(accuracy<<5u));
    uint32_t radio_mode=*(volatile uint8_t *)(record+440u);
    *(volatile uint8_t *)(packet+26u)=
        (uint8_t)(radio_mode==2u?2u:radio_mode==3u?4u:radio_mode==4u?8u:1u);
    uint32_t address_high=*(volatile uint32_t *)(record+20u);
    uint32_t address_low=*(volatile uint32_t *)(record+16u);
    (void)opencfw_em9305_radio_address_write_3045e8(packet+27u,address_low,address_high);
    *(volatile uint8_t *)(packet+33u)=*(volatile uint8_t *)(root+262u);
    *(volatile uint8_t *)(packet+34u)=*(volatile uint8_t *)(root+263u);
    custom=*(volatile uint8_t *)custom_slot;
    if(custom!=0u) {
        word=*(volatile uint32_t *)(record+784u);
        *(volatile uint8_t *)(packet+35u)=(uint8_t)word;
        word=*(volatile uint32_t *)(record+784u);
        *(volatile uint8_t *)(packet+36u)=(uint8_t)(word>>8u);
        *(volatile uint8_t *)(packet+37u)=(uint8_t)*(volatile uint16_t *)(record+786u);
        *(volatile uint8_t *)(packet+38u)=*(volatile uint8_t *)(record+787u);
        *(volatile uint8_t *)(packet+39u)=*(volatile uint8_t *)(record+788u);
        *(volatile uint8_t *)(packet+40u)=*(volatile uint8_t *)(record+789u);
        *(volatile uint8_t *)(packet+41u)=*(volatile uint8_t *)(record+796u);
        *(volatile uint8_t *)(packet+42u)=*(volatile uint8_t *)(record+797u);
    }
    return opencfw_em9305_phy_packet_send_32d32c(root,packet);
}
