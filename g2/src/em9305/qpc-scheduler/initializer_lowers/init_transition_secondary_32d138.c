#include <stdint.h>

extern uint32_t opencfw_em9305_init_secondary_allocate_316e74(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_radio_secondary_encode_32e164(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_radio_resolve_303bdc(
    uint32_t,uint32_t,uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_start_3213f8(uintptr_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_secondary_commit_321e14(uint32_t);
extern uint32_t opencfw_em9305_init_secondary_finish_321820(void);

static uint8_t rd8(uintptr_t p) { return *(volatile uint8_t *)p; }
static uint16_t rd16(uintptr_t p) { return *(volatile uint16_t *)p; }
static uint32_t rd32(uintptr_t p) { return *(volatile uint32_t *)p; }
static void wr8(uintptr_t p,uint32_t v) { *(volatile uint8_t *)p=(uint8_t)v; }
static void wr16(uintptr_t p,uint32_t v) { *(volatile uint16_t *)p=(uint16_t)v; }
static void wr32(uintptr_t p,uint32_t v) { *(volatile uint32_t *)p=v; }

/* Prepared native 0x32d138..0x32d2da.  The entry wrapper owns the native
 * 12-byte local descriptor.  Its unwritten bytes 8..10 retain the incoming
 * stack state; the resolver may inspect or overwrite this same frame. */
uint32_t opencfw_em9305_init_transition_secondary_32d138_body(uint8_t *local)
{
    uintptr_t message=rd32(0x805c80u);
    /* Native incoming R0=0x805c80 is overwritten before first use by the
     * source-owned 316e74 allocator; its canonical selected ABI is void. */
    uintptr_t record=opencfw_em9305_init_secondary_allocate_316e74();
    if(record==0u) return 0u;
    uintptr_t out=record+624u;
    (void)opencfw_em9305_common_request_30455c(1u);
    uint8_t flag33=rd8(message+33u),flag35=rd8(message+35u);
    uint32_t high=rd32(message+40u),low=rd32(message+36u);
    uint8_t flag32=rd8(message+32u);
    wr8(out+2u,flag33);
    wr8(out+152u,flag35);
    wr8(out,0u);
    wr16(out-8u,0u);
    wr8(record+9u,12u);
    wr32(0x8051d0u,(uint32_t)record);
    wr32(record+620u,1000u);
    wr32(record+632u,high);
    wr32(record+628u,low);
    /* Native writes out+1 in the encode call's delay slot. */
    wr8(out+1u,flag32);
    (void)opencfw_em9305_radio_secondary_encode_32e164(0x805fbcu,message+6u);

    uint32_t period=rd16(0x805fc0u);
    flag33=rd8(message+33u);
    high=rd32(message+40u);
    low=rd32(message+36u);
    flag32=rd8(message+32u);
    period=(uint32_t)((uint64_t)period*1250u);
    wr32(record+724u,high);
    wr32(record+720u,low);
    wr8(out+92u,flag32);
    wr8(out+93u,flag33);
    wr32(record+252u,period); /* BBIT0 delay slot executes both routes. */
    if((flag33&1u)!=0u && (high&0xc000u)==0x4000u) {
        wr32((uintptr_t)local,0u);
        wr32((uintptr_t)(local+4u),0u);
        local[11]=0u;
        if(opencfw_em9305_radio_resolve_303bdc(
               low,high,(uintptr_t)(local+11u),(uintptr_t)local)!=0u) {
            uint8_t classification=local[11];
            uint32_t resolved_high=*(uint32_t *)(void *)(local+4u);
            uint32_t resolved_low=*(uint32_t *)(void *)local;
            wr32(record+724u,resolved_high);
            wr32(record+720u,resolved_low);
            wr8(out+93u,(uint8_t)(classification|2u));
        }
    }
    uint32_t message_word=rd32(message+48u);
    uint8_t flag46=rd8(message+46u);
    wr32(record+508u,message_word);
    uint8_t b52=rd8(message+52u);
    wr8(out+153u,flag46);
    wr8(record+512u,b52);
    wr8(record+513u,rd8(message+53u));
    wr8(record+514u,rd8(message+54u));
    uint8_t b55=rd8(message+55u);
    uintptr_t current=rd32(0x8051d0u);
    wr8(record+515u,b55); /* BL delay slot before 3213f8. */
    (void)opencfw_em9305_init_secondary_start_3213f8(current);
    if(rd8(out+153u)!=0u) {
        uint32_t callback=rd32(0x805c90u);
        uint32_t global8c=rd32(0x805c8cu);
        uint32_t global84=rd32(0x805c84u);
        uint32_t global10=rd32(0x805c10u);
        uintptr_t target=rd32(record+92u);
        message_word=rd32(message+48u);
        wr32(record+76u,global8c);
        wr32(record+80u,global84);
        wr32(record+212u,global10);
        wr32(target+72u,message_word);
        if(callback!=0u)
            (void)((uint32_t (*)(uintptr_t))(uintptr_t)callback)(record);
    }
    (void)opencfw_em9305_command_count_30e4bc();
    uint16_t h24=rd16(message+24u),h4=rd16(message+4u);
    uint16_t h26=rd16(message+26u),h28=rd16(message+28u);
    uint16_t h44=rd16(message+44u);
    uint8_t b34=rd8(message+34u);
    uint16_t h30=rd16(message+30u);
    message_word=rd32(message+48u);
    b52=rd8(message+52u);
    uint8_t b53=rd8(message+53u),b54=rd8(message+54u);
    b55=rd8(message+55u);
    wr16(0x8051c2u,h24);
    wr16(0x8051c4u,h4);
    wr16(0x8051c6u,h26);
    wr16(0x8051c8u,h28);
    wr16(0x8051cau,h44);
    wr8(0x8051ccu,b34);
    wr16(0x8051ceu,h30);
    wr32(0x8051d4u,message_word);
    wr8(0x8051d8u,b52);
    wr8(0x8051d9u,b53);
    wr8(0x8051dau,b54);
    wr8(0x8051dbu,b55); /* BL delay slot before 321e14. */
    /* Native 321e14 reads only entry R0 (slot); R1-R3 are overwritten. */
    (void)opencfw_em9305_init_secondary_commit_321e14(h24);
    /* Native 321820 overwrites R0 before use; commit's result is ignored. */
    return opencfw_em9305_init_secondary_finish_321820();
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_secondary_32d138\n"
".type opencfw_em9305_init_transition_secondary_32d138,@function\n"
"opencfw_em9305_init_transition_secondary_32d138:\n"
"enter_s [r13-r17,fp,blink]\nsub_s sp,sp,0xc\n"
"mov r0,sp\nbl opencfw_em9305_init_transition_secondary_32d138_body\n"
"leave_s [r13-r17,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_secondary_32d138,. - opencfw_em9305_init_transition_secondary_32d138\n");
#else
uint32_t opencfw_em9305_init_transition_secondary_32d138(void)
{
    uint8_t local[12] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_secondary_32d138_body(local);
}
#endif
