#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x32b82c..0x32b9a4: start an associated (periodic) cycle for the
 * record. Stamp the object (+8) and record (+800) with the scheduled
 * start, seed the channel CRC (+706), count the usable channels of the
 * channel map (+1160 table, limited by +788) for event 30e858, then insert
 * the schedule entry, advancing the event index (+799, wrapping into the
 * counter +376) and re-timing the object (+8/+12) until it fits. Returns
 * the admissible byte of the selected channel or, when there is none, a
 * fresh 12-bit CRC seed that differs from the record's (+64) and the
 * previous one. The multiply-accumulate keeps only its low 32 bits. */
extern uint32_t opencfw_em9305_associated_time_alias_30fd34(void);
extern uint32_t opencfw_em9305_radio_schedule_313424(uint32_t incoming,
    uint32_t index,uint32_t timestamp,uint32_t existing,uint32_t action);
extern uint32_t opencfw_em9305_scan_random_30c478(void);
extern uint32_t opencfw_em9305_crc_update_304678(uint32_t state,uint32_t count,
                                                 uintptr_t input);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_associated_cycle_event_30e858(uint32_t value0,
    uint32_t value1,uint32_t value2);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t object,
                                                                 uintptr_t tie);
extern uint32_t opencfw_em9305_associated_channel_seed_324c98(uintptr_t channels,
                                                              uint32_t seed);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t selector);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t first,
                                                          uint32_t second);

static inline uint32_t r32(uintptr_t a){return *(volatile uint32_t *)a;}
static inline uint32_t r16(uintptr_t a){return *(volatile uint16_t *)a;}
static inline uint32_t r8(uintptr_t a){return *(volatile uint8_t *)a;}
static inline void w32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static inline void w16(uintptr_t a,uint32_t v){*(volatile uint16_t *)a=(uint16_t)v;}
static inline void w8(uintptr_t a,uint32_t v){*(volatile uint8_t *)a=(uint8_t)v;}

uint32_t opencfw_em9305_child_32b82c(uintptr_t record,uintptr_t object)
{
    uintptr_t packet=r32(object+44u);
    w16(packet+224u,0u);
    uint32_t now=opencfw_em9305_associated_time_alias_30fd34();
    int32_t offset=(int32_t)(record-r32(((uintptr_t)&em9305_ram_805be0 + 0x58u)));
    uint32_t row=(uint8_t)((uint32_t)(offset/2824)+4u);
    uint32_t elapsed=opencfw_em9305_radio_schedule_313424(r32(record+792u),row,
                                                          now,0u,0u);
    uint32_t stamp=now+elapsed;
    w32(object+8u,stamp);
    w32(record+800u,stamp);
    uint32_t crc=opencfw_em9305_crc_update_304678(
        opencfw_em9305_scan_random_30c478(),0u,0u);
    uintptr_t map=r32(record+1160u)+0xf08u;
    w16(record+706u,crc);
    uintptr_t destination=r32(record+2812u);
    uint32_t high=r32(map),low=r32(map-4u);
    w8(destination+78u,0u);
    uint32_t count=opencfw_em9305_ll_mask_count_30c414(low,high);
    uint32_t channels=r8(record+788u);
    if(count<channels){
        map=r32(record+1160u)+0xf08u;
        high=r32(map);
        low=r32(map-4u);
        channels=opencfw_em9305_ll_mask_count_30c414(low,high);
    }
    destination=r32(record+2812u);
    uint32_t id=r8(record+1u);
    w8(destination+79u,channels);
    (void)opencfw_em9305_associated_cycle_event_30e858(id,r8(destination+78u),channels);
    for(;;){
        uint32_t inserted=opencfw_em9305_associated_schedule_insert_312da4(object,0u);
        uint32_t index=r8(record+799u);
        if(inserted!=0u){
            uintptr_t table=r32(record+1160u);
            uint32_t previous=r16(record+706u);
            uint32_t selected=r8(table+(index&0x7fu)+0xf0cu);
            w8(packet+261u,0u);
            if(selected!=255u){
                uint32_t admissible=r8(table+(selected<<8));
                if(admissible!=0u)return admissible;
            }
            previous&=0xfffu;
            w16(record+1144u,0u);
            for(;;){
                crc=opencfw_em9305_crc_update_304678(
                    opencfw_em9305_scan_random_30c478(),0u,0u);
                uint32_t reference=r16(record+64u)&0xfffu;
                w16(record+706u,crc);
                if((crc&0xfffu)!=reference&&(crc&0xfffu)!=previous)return crc;
            }
        }
        uint32_t width=r8(record+788u);
        uint32_t next=index+1u;
        w8(record+799u,next);
        uint32_t counter;
        if((uint8_t)next==width){
            counter=r16(record+376u)+1u;
            next=0u;
            w8(record+799u,0u);
            w16(record+376u,counter);
        }else{
            counter=r16(record+376u);
        }
        uint32_t chosen=opencfw_em9305_associated_channel_seed_324c98(
            record+720u,(uint16_t)(counter^(uint8_t)next));
        uint32_t events=r16(record+376u);
        uint32_t interval=r32(record+700u);
        uint32_t local=r8(record+799u);
        uint32_t scaled=r32(record+792u);
        w8(record+697u,chosen);
        uint32_t product=interval*events+scaled*local;
        uint32_t factor=opencfw_em9305_mode_callback_child_317ea4(5u);
        uint32_t phase=opencfw_em9305_init_secondary_time_317ebc(product,factor);
        uint32_t old=r32(object+12u);
        w32(object+8u,stamp-phase+product);
        w32(object+12u,phase+old);
    }
}

/* Same stock function 0x32b82c; the former separate copy
 * (init_associated_cycle_start_32b82c.c) seeded the channel with the old
 * counter on index wrap, where stock uses counter+1. */
__typeof__(opencfw_em9305_child_32b82c) opencfw_em9305_associated_cycle_start_32b82c
    __attribute__((alias("opencfw_em9305_child_32b82c")));
