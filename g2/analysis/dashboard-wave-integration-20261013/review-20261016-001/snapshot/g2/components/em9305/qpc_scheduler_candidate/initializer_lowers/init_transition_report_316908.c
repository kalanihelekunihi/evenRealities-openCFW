#include <stdint.h>

extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);

/* Entire native 0x316908..0x316948. The first 36 bytes are cleared;
 * the native two-byte sentinel at offset 36 belongs to the 40-byte frame.
 * Bytes 38..39 retain native ambient stack contents through the ARC entry
 * frame below. The serializer writes six bytes at offset 10. */
uint32_t opencfw_em9305_init_transition_report_316908_body(
    uint32_t identity,uint32_t status,uint32_t fresh,
    uint32_t address_low,uint32_t address_high,uint8_t *frame)
{
    (void)opencfw_em9305_memset(frame,0u,36u);
    frame[36]=0xffu;
    frame[37]=0xffu;
    frame[35]=(uint8_t)identity;
    frame[9]=(uint8_t)fresh;
    frame[4]=(uint8_t)status;
    frame[3]=(uint8_t)status;
    frame[2]=5u; /* Native BL serializer delay slot executes before call. */
    (void)opencfw_em9305_radio_address_write_3045e8(
        (uintptr_t)(frame+10u),address_low,address_high);
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)frame);
}

#ifdef __arc__
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_transition_report_316908\n"
".type opencfw_em9305_init_transition_report_316908,@function\n"
"opencfw_em9305_init_transition_report_316908:\n"
"enter_s [r13-r17,fp,blink]\nsub_s sp,sp,0x28\n"
"mov r5,sp\nbl opencfw_em9305_init_transition_report_316908_body\n"
"leave_s [r13-r17,fp,blink,pcl]\n"
".size opencfw_em9305_init_transition_report_316908,. - opencfw_em9305_init_transition_report_316908\n");
#else
uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t identity,uint32_t status,uint32_t fresh,
    uint32_t address_low,uint32_t address_high)
{
    uint8_t frame[40] __attribute__((aligned(4)));
    return opencfw_em9305_init_transition_report_316908_body(
        identity,status,fresh,address_low,address_high,frame);
}
#endif
