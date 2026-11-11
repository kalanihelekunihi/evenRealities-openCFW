#include <stdint.h>

/* Native 0x304184..0x3041d8: prepare and bind the radio for a context, store
 * the session word +128 and context word +8 in the radio block at 0x8015c4,
 * load a 20-byte radio record (ROM template 0x3343f8 when the session word
 * +100 is set, zeros otherwise) and issue radio request 257 on 0x8013f0. */
extern uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t);
extern const uint8_t opencfw_em9305_radio_template_3343f8[20];
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_radio_record_30fc28(uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30faec(uintptr_t,uint32_t);

uint32_t opencfw_em9305_child_304184(uintptr_t context, uintptr_t radio)
{
    uint32_t frame[5];
    uintptr_t session = *(volatile uint32_t *)(context + 0x2cu);
    (void)opencfw_em9305_common_radio_prepare_30fb4c(radio);
    *(volatile uint32_t *)(uintptr_t)(0x8015c4u + 0x14u) = *(volatile uint32_t *)(session + 128u);
    *(volatile uint32_t *)(uintptr_t)(0x8015c4u + 0x10u) = *(volatile uint32_t *)(context + 8u);
    (void)opencfw_em9305_common_radio_bind_30fc10(0x8015c4u + 8u);
    *(volatile uint8_t *)(uintptr_t)0x8015c4u = 0u;
    if (*(volatile uint32_t *)(session + 0x64u) != 0u)
        (void)opencfw_em9305_memcpy(frame, opencfw_em9305_radio_template_3343f8, 20u);
    else
        (void)opencfw_em9305_memset(frame, 0u, 20u);
    (void)opencfw_em9305_radio_record_30fc28((uintptr_t)frame);
    return opencfw_em9305_radio_request_30faec(0x8013f0u, 257u);
}
