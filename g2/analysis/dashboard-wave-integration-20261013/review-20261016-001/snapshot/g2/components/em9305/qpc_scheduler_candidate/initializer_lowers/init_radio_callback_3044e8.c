#include <stdint.h>

/* Native 0x3044e8..0x30455c. R4 is the fifth incoming callback word. */
extern uint32_t opencfw_em9305_auxiliary_ready_303f68(void);
extern uint32_t opencfw_em9305_common_radio_prepare_30fb4c(uintptr_t);
extern uint32_t opencfw_em9305_common_radio_bind_30fc10(uintptr_t);
extern uint32_t opencfw_em9305_radio_request_30faec(uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_radio_followup_30fb3c(uint32_t, uint32_t);
extern uint32_t opencfw_em9305_common_radio_finish_3045c0(uint32_t);

static uint32_t load32(uintptr_t address)
{ return *(volatile uint32_t *)address; }
static void store32(uintptr_t address, uint32_t value)
{ *(volatile uint32_t *)address=value; }
static void store8(uintptr_t address, uint8_t value)
{ *(volatile uint8_t *)address=value; }

uint32_t opencfw_em9305_init_callback_3044e8(
    uintptr_t context, uint32_t second, uint32_t third,
    uint32_t fourth, uintptr_t callback)
{
    uint32_t current=load32(context);
    const uintptr_t radio=0x8015c4u;
    /* Native STB.AB writes at old R13, then advances R13 by eight. */
    store8(radio,1u);
    if (current==0u) {
        current=((uint32_t (*)(uint32_t,uint32_t,uint32_t,uint32_t,uintptr_t))callback)(
            current,second,third,fourth,callback);
        store32(context,current);
        if (current==0u)
            return opencfw_em9305_common_radio_finish_3045c0(current);
    }
    if (third==0u) {
        if (second!=0u) return current;
        return opencfw_em9305_radio_followup_30fb3c(current,36u);
    }
    uintptr_t owner=(uintptr_t)opencfw_em9305_auxiliary_ready_303f68();
    uintptr_t record=(uintptr_t)load32(owner+44u);
    uint32_t replacement=load32(record+72u);
    uint32_t old=load32(record+4u);
    store32(record+4u,replacement);
    (void)opencfw_em9305_common_radio_prepare_30fb4c(record);
    (void)load32(owner+44u); /* Native 0x304520 read precedes 0x304522. */
    uintptr_t fresh_record=(uintptr_t)load32(owner+44u);
    /* Two-operand native ASL r0,r16 copies fourth<<1 into R0. */
    uint32_t shifted=fourth<<1u;
    uint32_t combined=third+second;
    store32(radio+20u,shifted);
    store32(radio+16u,combined-fourth);
    store32(fresh_record+4u,old);
    (void)opencfw_em9305_common_radio_bind_30fc10(radio+8u);
    uint32_t request=load32(context);
    return opencfw_em9305_radio_request_30faec(request,257u);
}
