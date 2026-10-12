#include <stdint.h>

/* Whole native entry bodies in transition tables 0x335398 and 0x335730.
 * These are callable code identities, not synthetic interior-block targets. */
extern uint32_t opencfw_em9305_ll_schedule_notify_313354(uintptr_t);
extern uint32_t opencfw_em9305_init_secondary_cleanup_321450(uintptr_t);
extern uint32_t opencfw_em9305_init_transition_event_308664(uint32_t,
                                                              uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_wsf_timer_stop(uintptr_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern uint32_t opencfw_em9305_common_release_304588(uint32_t);
extern uint32_t opencfw_em9305_command_count_down_30e48c(void);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_init_transition_prepare_31a700(
    uintptr_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_command_advertising_error_30e758(uint32_t);
extern uint32_t opencfw_em9305_init_transition_gate_3168e4(void);
extern uintptr_t opencfw_em9305_init_transition_refresh_327dbc(void);
extern uint32_t opencfw_em9305_common_request_30455c(uint32_t);
extern uint32_t opencfw_em9305_command_count_30e4bc(void);
extern uint32_t opencfw_em9305_init_secondary_count_up_30e4cc(void);
extern uint32_t opencfw_em9305_init_transition_start_327b60(void);
extern uint32_t opencfw_em9305_init_state_count_down_30e49c(void);

/* Native 0x3168e4..0x316904, shared by two selector callbacks. */
uint32_t opencfw_em9305_init_transition_gate_3168e4(void)
{
    (void)opencfw_em9305_command_count_down_30e48c();
    uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805b9du;
    *(volatile uint8_t *)(uintptr_t)0x805a71u=0u;
    if(enabled!=0u)return opencfw_em9305_init_state_count_down_30e49c();
    return 0u;
}

/* Complete native entries from the 0x334b1c selector table. */
uint32_t opencfw_em9305_init_transition_316698(uintptr_t incoming)
{ (void)incoming;return opencfw_em9305_command_advertising_error_30e758(0u); }

uint32_t opencfw_em9305_init_transition_3166a0(uintptr_t incoming)
{
    (void)incoming;
    (void)opencfw_em9305_common_release_304588(1u);
    (void)opencfw_em9305_init_transition_gate_3168e4();
    (void)opencfw_em9305_init_transition_refresh_327dbc();
    return opencfw_em9305_command_advertising_error_30e758(0u);
}

uint32_t opencfw_em9305_init_transition_3166bc(uintptr_t incoming)
{ (void)incoming;return opencfw_em9305_command_advertising_error_30e758(12u); }

uint32_t opencfw_em9305_init_transition_3166c4(uintptr_t incoming)
{
    (void)incoming;
    (void)opencfw_em9305_common_release_304588(1u);
    (void)opencfw_em9305_init_transition_gate_3168e4();
    return opencfw_em9305_init_transition_refresh_327dbc();
}

uint32_t opencfw_em9305_init_transition_3166d8(uintptr_t incoming)
{
    (void)incoming;
    (void)opencfw_em9305_common_request_30455c(1u);
    (void)opencfw_em9305_command_count_30e4bc();
    uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805b9du;
    *(volatile uint8_t *)(uintptr_t)0x805a71u=1u;
    if(enabled!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
    return opencfw_em9305_init_transition_start_327b60();
}

uint32_t opencfw_em9305_init_transition_316894(uintptr_t incoming)
{
    (void)incoming;
    uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805a71u;
    if(enabled==0u)return 0u;
    *(volatile uint8_t *)(uintptr_t)0x8052fdu=1u; /* STB.AB writes old R0. */
    return opencfw_em9305_ll_schedule_notify_313354(0x805300u);
}

uint32_t opencfw_em9305_init_transition_3168b0(uintptr_t incoming)
{
    (void)incoming;
    (void)opencfw_em9305_common_request_30455c(1u);
    (void)opencfw_em9305_command_count_30e4bc();
    uint32_t enabled=*(volatile uint8_t *)(uintptr_t)0x805b9du;
    *(volatile uint8_t *)(uintptr_t)0x805a71u=1u;
    if(enabled!=0u)(void)opencfw_em9305_init_secondary_count_up_30e4cc();
    (void)opencfw_em9305_init_transition_start_327b60();
    return opencfw_em9305_command_advertising_error_30e758(0u);
}

/* Native 0x320068..0x320082, used by the table callback 0x31a408. */
uint32_t opencfw_em9305_init_transition_count_down_320068(void)
{
    (void)opencfw_em9305_common_release_304588(1u);
    uint32_t count=*(volatile uint8_t *)(uintptr_t)0x805a74u;
    *(volatile uint8_t *)(uintptr_t)0x805a74u=(uint8_t)(count-1u);
    return opencfw_em9305_command_count_down_30e48c();
}

uint32_t opencfw_em9305_init_transition_31a408(uintptr_t record)
{
    uintptr_t nested=*(volatile uint32_t *)(record+0xafcu);
    uint32_t index=*(volatile uint16_t *)(nested+94u);
    uintptr_t base=*(volatile uint32_t *)(uintptr_t)0x805c70u;
    (void)opencfw_em9305_receive_terminate_325c08(base+index*912u,77u);
    return opencfw_em9305_init_transition_count_down_320068();
}

uint32_t opencfw_em9305_init_transition_31a538(uintptr_t record)
{
    uintptr_t global=*(volatile uint32_t *)(uintptr_t)0x805c78u;
    uint32_t id=*(volatile uint8_t *)(record+1u);
    uint32_t r4=*(volatile uint32_t *)(global+28u);
    uint32_t r3=*(volatile uint32_t *)(global+24u);
    uint32_t r2=*(volatile uint8_t *)(global+32u);
    return opencfw_em9305_init_transition_report_316908(id,12u,r2,r3,r4);
}

uint32_t opencfw_em9305_init_transition_31a554(uintptr_t record)
{
    uintptr_t global=*(volatile uint32_t *)(uintptr_t)0x805c78u;
    uint32_t r3=*(volatile uint32_t *)(global+12u);
    uint32_t r2=*(volatile uint32_t *)(global+8u);
    uint32_t r5=*(volatile uint8_t *)(global+5u);
    uint32_t r4=*(volatile uint8_t *)(global+4u);
    uint32_t r1=*(volatile uint8_t *)(global+6u);
    uint32_t result=opencfw_em9305_init_transition_prepare_31a700(
        record,r1,r2,r3,r4,r5);
    if(result!=0u)return result;
    r3=*(volatile uint32_t *)(global+12u);
    r2=*(volatile uint32_t *)(global+8u);
    r1=*(volatile uint8_t *)(global+6u);
    uintptr_t output=0x802a54u;
    *(volatile uint8_t *)(output+9u)=0u;
    *(volatile uint32_t *)(output+4u)=r3;
    *(volatile uint32_t *)output=r2;
    *(volatile uint8_t *)(output+8u)=(uint8_t)r1;
    return (uint32_t)output;
}

uint32_t opencfw_em9305_init_transition_31a58c(uintptr_t record)
{
    uintptr_t nested=*(volatile uint32_t *)(record+0xafcu);
    uint32_t state=*(volatile uint8_t *)(nested+80u);
    if(state!=3u) {
        uintptr_t output=0x802a54u;
        uint32_t id=*(volatile uint8_t *)(record+1u);
        uint32_t r2=*(volatile uint8_t *)(output+8u);
        uint32_t r4=*(volatile uint32_t *)(output+4u);
        uint32_t r3=*(volatile uint32_t *)output;
        (void)opencfw_em9305_init_transition_report_316908(
            id,2u,r2,r3,r4);
    }
    return opencfw_em9305_init_transition_count_down_320068();
}

/* Native 0x30e988..0x30e9a0: exactly six initialized event bytes. */
uint32_t opencfw_em9305_init_transition_event_30e988(uint32_t id)
{
    _Alignas(4) uint8_t event[6];
    *(volatile uint16_t *)(void *)(event+4u)=(uint16_t)id;
    *(volatile uint32_t *)(void *)event=0x001f0000u;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)event);
}

uint32_t opencfw_em9305_init_transition_3249ac(uintptr_t record)
{
    *(volatile uint8_t *)(record+2u)=1u;
    return opencfw_em9305_ll_schedule_notify_313354(record+48u);
}

uint32_t opencfw_em9305_init_transition_3249b8(uintptr_t record)
{ return opencfw_em9305_init_secondary_cleanup_321450(record); }

uint32_t opencfw_em9305_init_transition_3249bc(uintptr_t record)
{
    *(volatile uint8_t *)(record+2u)=1u;
    (void)opencfw_em9305_ll_schedule_notify_313354(record+48u);
    (void)opencfw_em9305_wsf_timer_stop(record+700u);
    uint32_t delta=(uint32_t)(record-0x803d78u);
    uint32_t id=(uint8_t)((int32_t)delta/784);
    return opencfw_em9305_init_transition_event_30e988(id);
}

uint32_t opencfw_em9305_init_transition_32d0f4(uintptr_t incoming)
{
    (void)incoming;
    uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x8051d0u;
    *(volatile uint8_t *)(record+3u)=1u;
    return opencfw_em9305_ll_schedule_notify_313354(record+48u);
}

uint32_t opencfw_em9305_init_transition_32d108(uint32_t native_r0)
{ return native_r0; }

uint32_t opencfw_em9305_init_transition_32d10c(uintptr_t incoming)
{
    (void)incoming;
    uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x8051d0u;
    *(volatile uint8_t *)(record+3u)=1u;
    (void)opencfw_em9305_ll_schedule_notify_313354(record+48u);
    record=*(volatile uint32_t *)(uintptr_t)0x8051d0u;
    uint32_t index=*(volatile uint8_t *)(record+777u);
    return opencfw_em9305_init_transition_event_308664(62u,record,index);
}

uint32_t opencfw_em9305_init_transition_32d2dc(uintptr_t incoming)
{
    (void)incoming;
    uintptr_t record=*(volatile uint32_t *)(uintptr_t)0x8051d0u;
    uint32_t active=*(volatile uint8_t *)(record+3u);
    if(active!=0u)*(volatile uint8_t *)(record+3u)=0u;
    return opencfw_em9305_init_secondary_cleanup_321450(record);
}
