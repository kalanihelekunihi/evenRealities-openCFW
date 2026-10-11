/* MX25U/MSPI descendants at 0x4c0758, 0x4bfd44, 0x4bfd62,
 * 0x4c235c, 0x4c45a4. The CMDQ operations follow the pinned
 * AmbiqSuite release_sdk5p1p0-366b80e084 HAL and native 0x538e3c/8c. */
#include <stdint.h>

extern uint32_t g2_gpio_critical_save(void); /* 0x473940 */
extern void audio_delay_us_selected(uint32_t); /* 0x4807a0 */
extern uint32_t audio_uart_pin_mux_enable(uint32_t,uint32_t); /* 0x4c44bc */
extern uint32_t audio_uart_pin_mux_disable(uint32_t,uint32_t); /* 0x4c4530 */
extern uint32_t audio_uart_mux_bit_get(uint32_t,uint32_t); /* 0x4c37a8 */

static uint32_t get32(const void *p,uint32_t offset) {
    return *(const uint32_t *)(const void *)((const uint8_t *)p+offset);
}
static void put32(void *p,uint32_t offset,uint32_t value) {
    *(uint32_t *)(void *)((uint8_t *)p+offset)=value;
}
static uint32_t shift(uint32_t value,uint32_t amount) {
    return amount<32u ? value<<amount : 0u;
}
static volatile uint32_t *const mspi_transition_reg=(volatile uint32_t *)(uintptr_t)0x40004110u;
void audio_uart_font_mspi_transition(uint32_t module,uint32_t enabled,uint32_t configure,uint32_t field) {
    uint32_t saved=g2_gpio_critical_save();
    uint32_t bit=shift(1u,module*5u);
    if((uint8_t)enabled!=0u) {
        if((uint8_t)configure!=0u) {
            uint32_t value=*mspi_transition_reg;
            value &=~shift(30u,module*5u);
            value |=shift((uint8_t)field*2u,module*5u);
            *mspi_transition_reg=value;
        }
        *mspi_transition_reg |=bit;
        audio_delay_us_selected(10u);
    } else {
        *mspi_transition_reg &=~bit;
    }
    __asm volatile("msr primask, %0" : : "r"(saved) : "memory");
}

static uint32_t cmdq_valid(const void *q) {
    return q!=0 && (get32(q,0u)&0x01ffffffu)==0x01cdcdcdu;
}
/* Native CMDQ header word bit25 is bEnable; pReg is at +0x24 and its
 * first field is regCQCfg. */
static uint32_t cmdq_enable(void *q) {
    if(!cmdq_valid(q)) return 2u;
    uint32_t prefix=get32(q,0u);
    if(prefix&0x02000000u) return 0u;
    if(get32(q,8u)>=0x20080000u) __asm volatile("dmb sy" : : : "memory");
    volatile uint32_t *const *regs=(volatile uint32_t *const *)(uintptr_t)get32(q,0x24u);
    *regs[0] |=1u;
    put32(q,0u,prefix|0x02000000u);
    return 0u;
}
static uint32_t cmdq_disable(void *q) {
    if(!cmdq_valid(q)) return 2u;
    uint32_t prefix=get32(q,0u);
    if((prefix&0x02000000u)==0u) return 0u;
    volatile uint32_t *const *regs=(volatile uint32_t *const *)(uintptr_t)get32(q,0x24u);
    *regs[0] &=~1u;
    put32(q,0u,prefix&~0x02000000u);
    return 0u;
}
uint32_t audio_uart_font_mspi_suspend(void *device) {
    uint32_t pin=(uint8_t)(get32(device,4u)+16u);
    uint32_t status=audio_uart_pin_mux_enable(4u,pin);
    if(status!=0u) return status;
    return cmdq_enable((void *)(uintptr_t)get32(device,0x828u));
}
uint32_t audio_uart_font_mspi_resume(void *device) {
    return cmdq_disable((void *)(uintptr_t)get32(device,0x828u));
}
uint32_t audio_uart_font_power_prepare(void *device,uint32_t mask) {
    if(device==0 || (get32(device,0u)&0x01ffffffu)!=0x01bebebeu) return 2u;
    uint32_t module=get32(device,4u);
    volatile uint32_t *reg=(volatile uint32_t *)(uintptr_t)(0x40060200u+(module<<12u));
    *reg &=~mask;
    return 0u;
}
uint32_t audio_uart_font_pin_mux_disable(uint32_t pin) {
    pin=(uint8_t)pin;
    if(pin>=0x39u) return 6u;
    for(uint32_t group=0u;group<7u;group++) {
        if(audio_uart_mux_bit_get(group,pin)!=0u)
            (void)audio_uart_pin_mux_disable(group,pin);
    }
    return 0u;
}
