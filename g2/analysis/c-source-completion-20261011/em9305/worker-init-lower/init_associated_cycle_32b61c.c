#include <stdint.h>

/* Native 0x32b61c..0x32b828. Connected callbacks 32b618, 32b82c,
 * 32b9a4 remain genuine source children until their whole bodies are reduced. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_random_31896c(void);
extern uint32_t opencfw_em9305_radio_crc_seed_318960(void);
extern uint32_t opencfw_em9305_mode_callback_child_317ea4(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_time_317ebc(uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_callback_child_3246c0(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_object_init_312918(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_radio_duration_312be4(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_associated_slot_allocate_3133b4(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_slot_query_31b2fc(uint32_t,uintptr_t);
extern uint32_t opencfw_em9305_associated_packet_callback_32c69c(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_associated_cycle_tail_32b618(uintptr_t);
extern uint32_t opencfw_em9305_associated_cycle_callback_32b9a4(uintptr_t);
extern uint32_t opencfw_em9305_associated_cycle_start_32b82c(uintptr_t,uintptr_t);

static uint32_t read32(uintptr_t a){return *(volatile uint32_t *)a;}
static uint32_t read16(uintptr_t a){return *(volatile uint16_t *)a;}
static uint32_t read8(uintptr_t a){return *(volatile uint8_t *)a;}
static void write32(uintptr_t a,uint32_t v){*(volatile uint32_t *)a=v;}
static void write16(uintptr_t a,uint16_t v){*(volatile uint16_t *)a=v;}
static void write8(uintptr_t a,uint8_t v){*(volatile uint8_t *)a=v;}

uint32_t opencfw_em9305_init_callback_32b61c(uintptr_t record)
{
    uintptr_t object=record+380u;
    (void)opencfw_em9305_memset((void *)object,0u,148u);
    write8(record+406u,1u);
    write8(record+404u,1u);
    write32(record+412u,(uint32_t)(uintptr_t)opencfw_em9305_associated_cycle_tail_32b618);
    write32(record+408u,(uint32_t)(uintptr_t)opencfw_em9305_associated_cycle_callback_32b9a4);
    write32(record+416u,(uint32_t)record);
    write32(record+424u,(uint32_t)(record+428u));
    write32(record+420u,(uint32_t)(record+1144u));
    uint32_t random=opencfw_em9305_associated_random_31896c();
    int32_t power=*(volatile int8_t *)(record+60u);
    uint32_t channel=read8(record+697u);
    write8(record+696u,(uint8_t)random);
    write8(record+428u,8u);
    write8(record+429u,(uint8_t)channel);
    if(power==127)power=(int32_t)read8(0x805a9cu);
    uint32_t access=read32(record+372u);
    uint32_t source=read32(record+784u);
    write8(record+430u,(uint8_t)power);
    write32(record+432u,access);
    write32(record+500u,source);
    uint32_t crc=opencfw_em9305_radio_crc_seed_318960();
    write32(record+436u,crc);
    uint32_t mode=read8(record+63u);
    uint32_t radio_byte=read8(0x805bedu);
    write32(record+568u,(uint32_t)(record+1077u));
    write32(record+532u,(uint32_t)(record+1077u));
    uint32_t config=read32(0x805cacu);
    write8(record+440u,(uint8_t)mode);
    write8(record+441u,(uint8_t)mode);
    write8(record+442u,(uint8_t)radio_byte);
    uint32_t value_a=read8(record+796u);
    uint32_t value_b=read8(record+797u);
    uint32_t clipped=read8(config+24u);
    uint32_t callback_a=read32(0x805cc8u);
    uint32_t callback_b=read32(0x805cccu);
    uint32_t callback_c=read32(0x805ca0u);
    uint32_t callback_d=read32(0x805ca4u);
    uint32_t callback_e=read32(0x805c28u);
    if(clipped>10u)clipped=10u;
    write8(record+654u,(uint8_t)clipped);
    write32(record+588u,(uint32_t)(uintptr_t)opencfw_em9305_associated_packet_callback_32c69c);
    write16(record+1154u,0u);
    write32(record+580u,callback_a);
    write32(record+592u,callback_b);
    write32(record+596u,callback_c);
    write32(record+600u,callback_d);
    write32(record+660u,callback_e);
    write32(record+672u,value_a*1250u);
    write32(record+676u,value_b*125u);
    uint32_t selector=opencfw_em9305_mode_callback_child_317ea4(5u);
    uint32_t first=opencfw_em9305_init_secondary_time_317ebc(read32(record+672u),selector);
    write32(record+680u,first);
    uint32_t second=opencfw_em9305_init_secondary_time_317ebc(read32(record+676u),selector);
    uint32_t selected=read8(record+798u); /* 32b76c precedes second result store. */
    write32(record+684u,second);
    write8(record+656u,(uint8_t)selected);
    (void)opencfw_em9305_init_callback_child_3246c0(record+428u,selected);
    (void)opencfw_em9305_associated_object_init_312918(object,0u);
    config=read32(0x805cacu);
    uint32_t budget=read32(record+72u);
    uint32_t maximum=read32(record+712u);
    uint32_t minimum=read32(record+708u);
    uint32_t spacing=read16(config+20u);
    if(budget>spacing)spacing=budget;
    uint32_t timing=0u;
    if(read8(record+804u)!=0u) {
        uintptr_t callback=(uintptr_t)read32(0x801a14u);
        if(callback!=0u)timing=((uint32_t (*)(uintptr_t,uint32_t,uintptr_t))callback)(
            0x801a14u,budget,0x801a14u);
    }
    uint32_t size=read16(record+1144u);
    uint32_t phy=read8(record+63u);
    uint32_t duration=opencfw_em9305_radio_duration_312be4(
        phy,0u,timing,(uint16_t)spacing,size,0u,2u,5u);
    uint32_t extent=read32(record+392u);
    if(duration>extent)extent=duration;
    write32(record+392u,extent);
    if(maximum<duration)return 69u;
    if(duration>minimum)minimum=duration;
    int32_t delta=(int32_t)((uint32_t)record-read32(0x805c38u));
    uint32_t row=(uint8_t)(delta/2824+4);
    volatile uint32_t allocation;
    uint32_t success=opencfw_em9305_associated_slot_allocate_3133b4(
        row,1u,minimum,maximum,extent,(uintptr_t)&allocation,
        (uintptr_t)opencfw_em9305_associated_slot_query_31b2fc);
    if(success==0u)return 67u;
    uint32_t chosen=allocation;
    write32(record+700u,chosen);
    write32(record+400u,chosen);
    (void)opencfw_em9305_associated_cycle_start_32b82c(record,object);
    return 0u;
}
