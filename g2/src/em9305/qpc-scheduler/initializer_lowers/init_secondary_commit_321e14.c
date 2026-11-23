#include <stdint.h>
#include "em9305_ram.h"

extern uint32_t opencfw_em9305_init_secondary_channel_324c68(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_schedule_318ad8(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_auxiliary_elapsed_303f8c(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_secondary_current_303f5c(void);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_init_secondary_compare_3249e8(uintptr_t,uintptr_t);
extern const uint16_t opencfw_em9305_init_secondary_intervals_3357d0[8];

static uint32_t load32(uintptr_t p){return *(volatile uint32_t *)p;}
static uint32_t load16(uintptr_t p){return *(volatile uint16_t *)p;}
static uint32_t load8(uintptr_t p){return *(volatile uint8_t *)p;}
static void store32(uintptr_t p,uint32_t v){*(volatile uint32_t *)p=v;}
static void store16(uintptr_t p,uint32_t v){*(volatile uint16_t *)p=(uint16_t)v;}
static void store8(uintptr_t p,uint32_t v){*(volatile uint8_t *)p=(uint8_t)v;}

/* ARCv2 DSP MPYWHL / MPYWHUL: low word of a 32 x 16 product. */
static uint32_t mpywhl_321e14(uint32_t a,int32_t b)
{
    return a*(uint32_t)(int32_t)(int16_t)b;
}
static uint32_t mpywhul_321e14(uint32_t a,uint32_t b)
{
    return a*(uint32_t)(uint16_t)b;
}
/* Native DIVU d,d,c. A zero divisor traps: stock sets STATUS32.DZ at startup
 * and the EV_DivZero handler resets the chip; C division emits the same DIVU. */
static uint32_t divu_321e14(uint32_t numerator,uint32_t denominator)
{
    return numerator/denominator;
}

/* Prepared full CFG candidate for native 0x321e14..0x322176. This unit is
 * deliberately separate from selected source pending native whole-body
 * review. R0 is the only live entry argument; R1-R3 are overwritten. */
uint32_t opencfw_em9305_init_secondary_commit_321e14(uint32_t slot)
{
    uintptr_t slots=load32(((uintptr_t)&em9305_ram_805c5c + 0x14u));
    uintptr_t slot_record=slots+(uint16_t)slot*912u;
    uintptr_t shared=((uintptr_t)&em9305_ram_8051b8 + 0x8u);
    uintptr_t record=load32(shared+16u);
    uintptr_t config=((uintptr_t)&em9305_ram_805fb8 + 0x4u);
    uintptr_t reference=record+690u;
    uintptr_t channel=record+644u;
    uint32_t kind=load8(slot_record+614u);
    if(kind==3u){
        store8(record+7u,1u);
        for(uint32_t i=0u;i<15u;i++)store16(record+280u+i*2u,0xfffu);
    }else if(kind==1u)store8(record+6u,1u);
    store8(record+256u,load8(config+16u));
    store32(record+648u,load32(config+12u));
    uint32_t interval=load16(slot_record+618u);
    uint32_t slot_half=load16(slot_record+616u);
    uint32_t config8=load32(config+8u);
    store16(record+616u,slot_half);
    store8(reference,1u);
    store32(record+644u,config8);
    store32(record+620u,interval*10u);
    (void)opencfw_em9305_init_secondary_channel_324c68(channel);
    uint32_t timing=load32(config+20u);
    uint32_t type=load8(config+3u);
    uint32_t enabled=load8(config+2u);
    uint32_t next=load32(config+24u);
    uint32_t baseline=load8(reference+86u);
    uint32_t period=load16(config);
    uint32_t current=load16(shared+6u);
    uint32_t mixed=(timing>>16u)^timing;
    store32(record+100u,timing);
    /* Native MPYD acc=type*0x258000 then MAC acc+=choice*period: low word. */
    uint32_t accumulation=type*0x258000u+(enabled?300u:30u)*period;
    store16(reference+2u,mixed);
    store32(record+104u,next);
    store8(record+109u,baseline);
    store8(record+108u,baseline);
    uint32_t first_time=opencfw_em9305_init_secondary_schedule_318ad8(
        slot_record,current);
    accumulation+=first_time;
    uint32_t second_time=opencfw_em9305_init_secondary_schedule_318ad8(
        slot_record,load16(slot_record+262u));
    uint32_t slot_now=load16(slot_record+262u);
    uint32_t current_now=load16(shared+6u);
    uint32_t anchor=load16(config+28u);
    uint32_t multiplier=load16(slot_record+266u);
    uint32_t base=load32(slot_record+28u);
    uint32_t divisor=load32(record+252u);
    uint32_t difference=(uint16_t)(current_now-slot_now);
    uint32_t adjusted,starting;
    if(difference<0x7fffu){
        uint32_t step=divu_321e14(
            mpywhl_321e14((uint32_t)(uint16_t)difference*(uint16_t)multiplier,1250)+base,divisor);
        adjusted=anchor-step;
        starting=accumulation-step*divisor;
    }else{
        uint32_t backward=slot_now-current_now;
        uint32_t step=divu_321e14(
            mpywhl_321e14((uint32_t)(uint16_t)backward*(uint16_t)multiplier,1250)+base,divisor);
        adjusted=anchor+step+1u;
        starting=(step+1u)*divisor+accumulation;
    }
    uint32_t elapsed=opencfw_em9305_auxiliary_elapsed_303f8c(
        starting,second_time);
    uint32_t active_before=load8(reference+87u);
    store16(record+248u,adjusted);
    if(active_before!=0u){
        uintptr_t outer=load32(record+780u);
        store32(outer+16u,0u);
    }
    uint32_t seed=opencfw_em9305_associated_channel_seed_324c98(
        channel,(uint16_t)adjusted);
    uint32_t first_index=load8(config+16u);
    uint32_t second_index=load8(shared+12u);
    uint32_t first_table=opencfw_em9305_init_secondary_intervals_3357d0[
        first_index>6u?7u:first_index];
    uint32_t second_table=opencfw_em9305_init_secondary_intervals_3357d0[
        second_index>6u?7u:second_index];
    store8(record+97u,seed);
    uintptr_t object=record+48u; /* Native saves pre-call R0 at SP+8. */
    uint32_t aux=opencfw_em9305_init_secondary_current_303f5c();
    uint32_t half14=load16(shared+14u);
    uint32_t fresh_divisor=load32(record+252u);
    uint32_t signed_delta=adjusted-half14;
    uint32_t delta=(uint16_t)signed_delta;
    uint32_t gated=(delta>=0x7fffu)?0u:signed_delta;
    uint32_t fp_product=mpywhul_321e14(fresh_divisor,gated);
    uint32_t saved=aux+first_table;
    uint32_t left=opencfw_em9305_init_secondary_time_317ebc(fp_product,saved);
    uint32_t shared10=load16(shared+10u);
    uint32_t shared8=load16(shared+8u);
    uint32_t other_raw=shared8-shared10;
    uint32_t other=(uint16_t)other_raw;
    uint32_t other_gated=(other>=0x7fffu)?0u:other_raw;
    uint32_t factor=load16(slot_record+266u);
    uint32_t right=opencfw_em9305_init_secondary_time_317ebc(
        mpywhl_321e14((uint32_t)(uint16_t)other_gated*(uint16_t)factor,1250),aux+second_table);
    uint32_t total=opencfw_em9305_init_secondary_time_317ebc(
        left+right,first_table+aux+second_table+1u);
    uint32_t fresh_enabled=load8(config+2u);
    uint32_t current_half=load16(record+248u);
    uint32_t future=elapsed+second_time;
    store32(record+272u,future);
    store16(record+278u,current_half);
    store16(record+276u,current_half);
    uint32_t advance_plus16=total+16u;
    store32(record+56u,future-advance_plus16);
    uint32_t base_period=fresh_enabled?300u:30u;
    uint32_t finish=base_period+2u*advance_plus16;
    store32(record+268u,finish);
    store32(record+204u,finish);
    (void)opencfw_em9305_associated_object_init_312918(object,0u);
    uint32_t active_after_init=load8(reference+87u);
    uint32_t schedule_start=load32(record+60u);
    store32(record+264u,schedule_start);
    uint32_t pace=0u;
    if(active_after_init!=0u){
        uint32_t upper=load8(reference-177u);
        uint32_t lower=load8(reference-178u);
        uint32_t current_period=load32(record+252u);
        pace=mpywhl_321e14(lower*upper,-1250)+current_period;
    }
    uint32_t active_count=0u,inactive_count=0u,iteration_count=0u;
    for(;;){
        uint32_t result=opencfw_em9305_associated_schedule_insert_312da4(
            object,(uintptr_t)&opencfw_em9305_init_secondary_compare_3249e8);
        if(result!=0u)return result;
        if(load8(reference+87u)!=0u){
            uintptr_t outer=load32(record+780u);
            uint32_t tick=load8(outer+18u)+1u;
            store8(outer+18u,tick);
            if((tick&0x7fu)==load8(reference-178u)){
                uint32_t half=load16(record+248u);
                active_count++;
                store8(outer+18u,0u);
                store16(record+248u,half+1u);
            }
            uint32_t table_byte=load8(record+513u);
            uint32_t ordinal=++iteration_count;
            uint32_t phase=mpywhul_321e14(table_byte,ordinal);
            phase=mpywhl_321e14(phase,1250)+active_count*pace;
            uint32_t advance=opencfw_em9305_init_secondary_time_317ebc(
                phase+fp_product+right,saved);
            advance=opencfw_em9305_init_secondary_time_317ebc(
                advance,first_table+aux+second_table+1u);
            uint32_t prior=load32(record+264u);
            uint32_t next_period=load32(record+268u);
            uint32_t previous_future=load32(record+272u);
            uintptr_t fresh_outer=load32(record+780u);
            uint32_t current_half=load16(record+248u);
            uint32_t current_tick=load8(fresh_outer+18u);
            store32(record+56u,previous_future-advance+phase-16u);
            store32(record+60u,prior+advance+16u);
            store32(record+204u,next_period+2u*advance+32u);
            seed=opencfw_em9305_associated_channel_seed_324c98(
                channel,current_tick^current_half);
            store8(record+97u,seed);
        }else{
            uint32_t next_slot=load16(record+248u)+1u;
            store16(record+248u,next_slot);
            seed=opencfw_em9305_associated_channel_seed_324c98(
                channel,(uint16_t)next_slot);
            uint32_t current_period=load32(record+252u);
            uint32_t ordinal=++inactive_count;
            store8(record+97u,seed);
            uint32_t phase=mpywhul_321e14(current_period,ordinal);
            uint32_t advance=opencfw_em9305_init_secondary_time_317ebc(
                phase+fp_product+right,saved);
            advance=opencfw_em9305_init_secondary_time_317ebc(
                advance,first_table+aux+second_table+1u);
            uint32_t previous_future=load32(record+272u);
            uint32_t prior=load32(record+264u);
            uint32_t next_period=load32(record+268u);
            store32(record+56u,phase-advance+previous_future-16u);
            store32(record+60u,prior+advance+16u);
            store32(record+204u,next_period+2u*advance+32u);
        }
    }
}
