#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "associated_312918_regs.h"

extern uint32_t opencfw_em9305_associated_object_init_with_regs_312918(
    uintptr_t object, uint32_t requested,
    struct opencfw_associated_312918_regs *regs);

static uint8_t object[64] __attribute__((aligned(4)));
static uint8_t packet[160] __attribute__((aligned(4)));
static uint16_t length;
static uint32_t last_size;
static uint32_t last_piece_size;
static uint32_t duration_calls;

static void w32(uint8_t *base, unsigned off, uint32_t value)
{ memcpy(base+off,&value,sizeof value); }
static uint32_t r32(uint8_t *base, unsigned off)
{ uint32_t value;memcpy(&value,base+off,sizeof value);return value; }

uint32_t opencfw_em9305_radio_duration_piece_312b88(
    uint32_t phy,uint32_t mode,uint32_t size)
{ last_piece_size=size;return 100u+phy+mode+size; }
uint32_t opencfw_em9305_radio_duration_312be4(
    uint32_t phy,uint32_t requested,uint32_t timing,uint32_t spacing,
    uint32_t size,uint32_t extended,uint32_t mode,uint32_t overhead)
{
    (void)phy;(void)requested;(void)timing;(void)spacing;(void)extended;
    (void)mode;(void)overhead;
    duration_calls++;
    last_size=size;
    return 1000u+size;
}
uint32_t opencfw_em9305_auxiliary_guard_interval(void){return 40u;}
uint32_t opencfw_em9305_channel_timing_adjust_312c5c(uint32_t x)
{return x+3u;}

int main(void)
{
    w32(object,40u,(uint32_t)(uintptr_t)&length);
    w32(object,44u,(uint32_t)(uintptr_t)packet);
    const unsigned sizes[]={0u,1u,64u,252u,253u,494u,500u,65535u};
    for(unsigned i=0;i<sizeof sizes/sizeof sizes[0];++i){
        memset(packet,0,sizeof packet);
        packet[0]=8u;
        length=(uint16_t)sizes[i];
        struct opencfw_associated_312918_regs regs={0x55aa55aau,0u,41u,42u,43u,44u};
        uint32_t r0=opencfw_em9305_associated_object_init_with_regs_312918(
            (uintptr_t)object,0u,&regs);
        uint32_t effective=sizes[i]<64u?64u:sizes[i];
        uint32_t expected=effective<=252u?effective+5u:
            (effective%247u==0u?257u:(effective%247u)+5u);
        assert(regs.r2==expected);
        assert(last_size==effective);
        assert(r0==1000u+effective);
        assert(r32(object,12u)==r0);
        assert(regs.r3==r32(object,12u));
        assert(regs.r4==effective && regs.r5==0u);
        assert(regs.r6==packet[14] && regs.r7==0u);
    }
    assert(duration_calls==sizeof sizes/sizeof sizes[0]);
    packet[0]=9u;
    struct opencfw_associated_312918_regs regs={0x55aa55aau,0u,41u,42u,43u,44u};
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==5u && last_size==0u);
    assert(regs.r4==0u && regs.r5==0u && regs.r6==packet[14] && regs.r7==0u);
    packet[0]=2u;w32(packet,104u,0u);
    regs.r2=0x55aa55aau;regs.r4=41u;regs.r5=42u;regs.r6=43u;regs.r7=44u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0x55aa55aau);
    assert(regs.r4==41u && regs.r5==42u && regs.r6==43u && regs.r7==44u);
    packet[0]=3u;w32(packet,104u,0u);
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0u);
    packet[0]=2u;w32(packet,104u,1u);packet[149]=57u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==57u);
    packet[0]=3u;packet[127]=3u;w32(packet,104u,1u);
    w32(packet,108u,0u);
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0xc10u);
    w32(packet,108u,1u);packet[149]=65u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==65u);
    packet[0]=6u;packet[132]=0u;w32(packet,100u,0u);
    regs.r2=0x55aa55aau;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0x55aa55aau);
    w32(packet,100u,1u);packet[124]=88u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==88u);
    packet[132]=1u;w32(packet,100u,0u);
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==36u);
    w32(packet,100u,1u);
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==400u); /* kind!=3 follows 312abc. */
    packet[13]=3u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==36u);
    packet[13]=0u;
    packet[0]=7u;w32(packet,116u,0u);w32(packet,100u,0u);
    length=0u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==13u);
    length=300u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==72u);
    length=482u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0u);
    length=40000u;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,50000u,&regs);
    assert(regs.r2==(uint32_t)(int32_t)(int16_t)40013u);
    assert(last_piece_size==regs.r2); /* EXTH_S output, not uint16 input. */
    packet[0]=1u;
    regs.r2=0x55aa55aau;
    (void)opencfw_em9305_associated_object_init_with_regs_312918(
        (uintptr_t)object,0u,&regs);
    assert(regs.r2==0x55aa55aau);
    assert(regs.r3==r32(object,12u));
    puts("312918 typed R2/R3: 8 lengths and 16 branch routes PASS");
    return 0;
}
