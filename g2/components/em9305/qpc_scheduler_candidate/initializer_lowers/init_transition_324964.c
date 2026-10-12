#include <stdint.h>

extern uint32_t opencfw_em9305_init_secondary_fill_324768(uintptr_t,uint8_t *);
extern uint32_t opencfw_em9305_init_secondary_event_30e928(
    uint32_t,uint32_t,uint8_t *,uint32_t);
extern uint32_t opencfw_em9305_init_transition_event_308664(
    uint32_t,uintptr_t,uint32_t);

/* Native 0x324964..0x3249a8. The 20-byte local response is reserved by
 * the ARC entry on every branch; selected fill owns its initialized bytes. */
uint32_t opencfw_em9305_init_transition_324964_body(
    uintptr_t record,uint8_t *response)
{
    uint8_t state=*(volatile uint8_t *)(record+9u);
    if(state==12u) {
        uint32_t feature=*(volatile uint8_t *)(record+777u);
        return opencfw_em9305_init_transition_event_308664(
            0u,record,feature);
    }
    if(state!=11u)return state;
    (void)opencfw_em9305_init_secondary_fill_324768(record,response);
    uint32_t id=(uint8_t)((int32_t)(record-0x803d78u)/784);
    uint32_t feature=*(volatile uint8_t *)(record+777u);
    return opencfw_em9305_init_secondary_event_30e928(
        0u,id,response,feature);
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_324964\n"
".type opencfw_em9305_init_transition_324964,@function\n"
"opencfw_em9305_init_transition_324964:\n"
"enter_s [r13,fp,blink]\nsub_s sp,sp,0x14\n"
"mov r1,sp\nbl opencfw_em9305_init_transition_324964_body\n"
"leave_s [r13,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_324964,. - opencfw_em9305_init_transition_324964\n");
#else
uint32_t opencfw_em9305_init_transition_324964(uintptr_t record)
{
    uint8_t response[20] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_324964_body(record,response);
}
#endif
