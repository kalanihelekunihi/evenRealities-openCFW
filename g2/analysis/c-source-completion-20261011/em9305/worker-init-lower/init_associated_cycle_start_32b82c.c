#include <stdint.h>

/* Native 0x32b82c..0x32b9a2. MAC is the BL.D delay instruction at 32b936,
 * so it executes before the 317ea4 child, preserving the ACC lifetime. */
extern uint32_t opencfw_em9305_pal_current_time(void);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_pal_random_step(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t,uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t,uint32_t,uint32_t);

static uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

static void native_mpyd_32b82c(uint32_t a,uint32_t b)
{__asm__ volatile("mpyd 0,%0,%1"::"r"(a),"r"(b):"r58","r59","memory");}
static uint32_t native_mac_32b82c(uint32_t a,uint32_t b)
{uint32_t out;__asm__ volatile("mac %0,%1,%2":"=r"(out):"r"(a),"r"(b):"r58","r59","memory");return out;}

uint32_t opencfw_em9305_associated_cycle_start_32b82c(uintptr_t record,uintptr_t object)
{
    uintptr_t packet=r32(object+44u);
    w16(packet+224u,0u); /* BL 30fd34 delay slot. */
    uint32_t now=opencfw_em9305_pal_current_time();
    uint32_t base=r32(0x805c38u);
    int32_t difference=(int32_t)((uint32_t)record-base);
    uint32_t row=(uint8_t)((uint32_t)(difference/2824)+4u);
    uint32_t scaled=r32(record+792u);
    uint32_t elapsed=opencfw_em9305_radio_schedule_313424(scaled,row,now,0u,0u);
    uint32_t stamp=now+elapsed;
    w32(object+8u,stamp);
    w32(record+800u,stamp); /* Random BL.D delay slot runs before the callee. */
    uint32_t random=opencfw_em9305_pal_random_step();
    uint32_t crc=opencfw_em9305_crc_update_304678(random,0u,0u);
    uintptr_t table=record+1160u;
    uint32_t bitmap_source=r32(table);
    w16(record+706u,crc);
    uintptr_t first=bitmap_source+0xf08u;
    uintptr_t destination=r32(record+2812u);
    uint32_t high=r32(first),low=r32(first-4u);
    w8(destination+78u,0u); /* First mask-count BL delay slot. */
    uint32_t count=opencfw_em9305_ll_mask_count_30c414(low,high);
    uint32_t limit=r8(record+788u);
    uint32_t channel_count=limit; /* R2 is the limit unless the second count runs. */
    if(count<limit){
        uintptr_t second=r32(record+1160u)+0xf08u;
        high=r32(second);
        low=r32(second-4u); /* Second BL delay slot. */
        channel_count=opencfw_em9305_ll_mask_count_30c414(low,high);
    }
    destination=r32(record+2812u);
    uint32_t id=r8(record+1u);
    w8(destination+79u,channel_count);
    (void)opencfw_em9305_associated_cycle_event_30e858(id,r8(destination+78u),channel_count);
    uintptr_t channel_state=record+720u;
    for(;;){
        uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(object,0u);
        uint32_t index=r8(record+799u); /* BL delay slot. */
        if(inserted!=0u){
            uintptr_t choices=r32(record+1160u);
            uint32_t current=index&127u;
            uint32_t previous=r16(record+706u);
            uint32_t selected=r8(choices+current+0xf0cu);
            w8(packet+261u,0u);
            if(selected!=255u){
                uint32_t admissible=r8(choices+(selected<<8u));
                if(admissible!=0u)return admissible;
            }
            previous&=4095u;
            w16(record+1144u,0u);
            for(;;){
                random=opencfw_em9305_pal_random_step();
                crc=opencfw_em9305_crc_update_304678(random,0u,0u);
                uint32_t reference=r16(record+64u)&4095u;
                w16(record+706u,crc);
                if((crc&4095u)!=reference && (crc&4095u)!=previous)return crc;
            }
        }
        uint32_t next=(uint8_t)(index+1u);
        uint32_t width=r8(record+788u);
        w8(record+799u,next); /* BRNE.D delay store. */
        uint32_t counter;
        if(next==width){
            counter=r16(record+376u);
            w8(record+799u,0u);
            w16(record+376u,counter+1u);
        }else counter=r16(record+376u);
        uint32_t seed=(uint16_t)((counter^next)&0xffffu);
        uint32_t chosen=opencfw_em9305_associated_channel_seed_324c98(channel_state,seed);
        uint32_t latest_count=r16(record+376u);
        uint32_t interval=r32(record+700u);
        uint32_t local_index=r8(record+799u);
        uint32_t scaled_time=r32(record+792u);
        native_mpyd_32b82c(interval,latest_count);
        w8(record+697u,chosen);
        uint32_t product=native_mac_32b82c(scaled_time,local_index);
        uint32_t factor=opencfw_em9305_mode_callback_child_317ea4(5u);
        uint32_t phase=opencfw_em9305_init_secondary_time_317ebc(product,factor);
        uint32_t old_object_time=r32(object+12u);
        uint32_t new_time=stamp-phase+product;
        uint32_t new_phase=phase+old_object_time;
        w32(object+8u,new_time);
        w32(object+12u,new_phase);
    }
}
