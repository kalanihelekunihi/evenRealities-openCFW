#include <stdint.h>

extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t,uint32_t,uint32_t);
extern void *opencfw_em9305_memcpy(void *,const void *,uint32_t);

/* Native 0x3239b8..0x3239d2. The initial count is captured in R15;
 * a second count read after the serializer controls the actual copy. */
uint32_t opencfw_em9305_init_transition_record_3239b8(
    uintptr_t output,uint32_t low,uint32_t high,uintptr_t record)
{
    uint8_t original=*(volatile uint8_t *)(record+31u);
    (void)opencfw_em9305_radio_address_write_3045e8(output,low,high);
    uint8_t current=*(volatile uint8_t *)(record+31u);
    (void)opencfw_em9305_memcpy((void *)(output+6u),(const void *)record,
        current);
    return (uint8_t)(original+6u);
}

/* Native 0x3243dc is an unconditional tail branch to 0x3239b8. */
uint32_t opencfw_em9305_init_transition_segment_3243dc(
    uintptr_t output,uint32_t low,uint32_t high,uintptr_t record)
{
    return opencfw_em9305_init_transition_record_3239b8(
        output,low,high,record);
}

/* Native 0x323c78..0x323c90: two six-byte address serializations. */
uint32_t opencfw_em9305_init_transition_record_323c78(
    uintptr_t output,uint32_t first_low,uint32_t first_high,
    uint32_t second_low,uint32_t second_high)
{
    (void)opencfw_em9305_radio_address_write_3045e8(
        output,first_low,first_high);
    (void)opencfw_em9305_radio_address_write_3045e8(
        output+6u,second_low,second_high);
    return 12u;
}
