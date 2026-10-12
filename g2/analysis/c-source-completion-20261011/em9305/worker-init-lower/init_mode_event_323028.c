#include <stdint.h>

/* Native 0x323028..0x3230de; fourteen-word ABI, eight registers plus six
 * caller-stack words. The 48-byte local record has native ambient bytes
 * outside the explicitly zeroed 10..34 range and named stores. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(
    uintptr_t output,uint32_t low,uint32_t high);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t event);
uint32_t opencfw_em9305_mode_event_323028(
    uint32_t index,uint32_t zero,uintptr_t config_plus4,uint32_t config_byte52,
    uint32_t config_word60,uint32_t config_word64,uint32_t config_word68,
    uint32_t config_word72,uint32_t config_word76,uint32_t config_word80,
    uint32_t zero_stack,uint32_t context_byte321,uint32_t context_byte890,
    uint32_t context_halfword892)
{
    _Alignas(4) uint8_t record[48];
    *(volatile uint8_t *)(record+8u)=(uint8_t)zero;
    *(volatile uint16_t *)(void *)(record+6u)=(uint16_t)index;
    *(volatile uint16_t *)(void *)record=(uint16_t)index;
    *(volatile uint8_t *)(record+9u)=(uint8_t)config_byte52;
    *(volatile uint8_t *)(record+2u)=5u;
    *(volatile uint8_t *)(record+4u)=(uint8_t)zero_stack;
    (void)opencfw_em9305_memset(record+10u,0u,25u);
    *(volatile uint8_t *)(record+3u)=(uint8_t)zero_stack;
    *(volatile uint16_t *)(void *)(record+36u)=(uint16_t)context_halfword892;
    *(volatile uint8_t *)(record+35u)=(uint8_t)context_byte890;
    if (config_plus4!=0u) {
        uint32_t word=*(volatile uint32_t *)(config_plus4+32u);
        uint16_t half=*(volatile uint16_t *)(config_plus4+36u);
        uint8_t byte=*(volatile uint8_t *)(config_plus4+43u);
        *(volatile uint32_t *)(void *)(record+16u)=word;
        *(volatile uint16_t *)(void *)(record+20u)=half;
        *(volatile uint8_t *)(record+22u)=byte;
    }
    (void)opencfw_em9305_radio_address_write_3045e8(
        (uintptr_t)(record+10u),config_word60,config_word64);
    (void)opencfw_em9305_radio_address_write_3045e8(
        (uintptr_t)(record+29u),config_word68,config_word72);
    (void)opencfw_em9305_radio_address_write_3045e8(
        (uintptr_t)(record+23u),config_word76,config_word80);
    uint32_t result=opencfw_em9305_ll_event_callback_30e79c((uintptr_t)record);
    if (zero_stack!=0u) return result;
    uint32_t flags=*(volatile uint8_t *)(uintptr_t)0x805a95u;
    if ((flags&(1u<<6u))==0u) return 33u;
    *(volatile uint16_t *)(void *)(record+42u)=33u;
    *(volatile uint16_t *)(void *)(record+44u)=(uint16_t)index;
    *(volatile uint16_t *)(void *)(record+40u)=(uint16_t)index;
    *(volatile uint8_t *)(record+46u)=(uint8_t)context_byte321;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)(record+40u));
}
