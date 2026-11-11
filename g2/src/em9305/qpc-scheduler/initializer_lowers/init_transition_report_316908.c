#include <stdint.h>

/* Native 0x316908..0x316948: report LL event 5 (address resolution
 * transition) in a 40-byte frame: bytes 0..35 cleared, {5, status,
 * status} at +2, fresh flag at +9, the 48-bit address serialised at +10,
 * identity at +35 and a 0xffff sentinel at +36. Bytes 38..39 are not
 * written (ambient stack contents, as in the native frame). */
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);

uint32_t opencfw_em9305_init_transition_report_316908(
    uint32_t identity,uint32_t status,uint32_t fresh,
    uint32_t address_low,uint32_t address_high)
{
    uint8_t frame[40] __attribute__((aligned(4)));
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
