/* Native pin-group bitset helpers 0x4c37a8/0x4c37fe and simple
 * group0/1 on/off bodies 0x4c3bfc/0x4c3c2e/0x4c3c60/0x4c3ca2. */
#include <stdbool.h>
#include <stdint.h>

extern volatile uint8_t *const audio_uart_mux_bitset; /* DAT_004c43dc */
extern const volatile uint8_t *const audio_uart_mux_capabilities; /* DAT_004c43e8 */
extern const uint32_t audio_uart_mux_group3_active_pin; /* *DAT_004c4678 */
extern const uint32_t audio_uart_mux_group3_idle_pin; /* *DAT_004c467c */
extern uint32_t g2_gpio_critical_save(void); /* selected 0x473940 */
extern bool g2_log_is_privileged(void); /* selected privilege test */
extern uint32_t g2_codec_pin_function(uint32_t,uint32_t); /* selected 0x480f0c */
extern volatile uint32_t *const audio_uart_mux_group4_power_word; /* DAT_004d3a08 */
uint32_t audio_uart_mux_group4_power(uint32_t enabled);

uint32_t audio_uart_mux_bit_get(uint32_t group,uint32_t pin) {
    volatile uint32_t *word=(volatile uint32_t *)(void *)(audio_uart_mux_bitset+
                     (uint8_t)group*8u+((uint8_t)pin>>5)*4u);
    return (*word>>((uint8_t)pin&31u))&1u;
}
uint32_t audio_uart_mux_bit_set(uint32_t group,uint32_t pin,uint32_t enabled) {
    group=(uint8_t)group;pin=(uint8_t)pin;
    if(group>=7u || pin>=0x39u) return 6u;
    volatile uint32_t *word=(volatile uint32_t *)(void *)(audio_uart_mux_bitset+
                                              group*8u+(pin>>5)*4u);
    uint32_t mask=1u<<(pin&31u);
    if(enabled==0u) *word &=~mask;
    else *word |=mask;
    return 0u;
}
uint32_t audio_uart_mux_any(uint32_t group) { /* native 0x4c377a */
    for(uint32_t word=0;word<2u;word++) {
        volatile uint32_t *p=(volatile uint32_t *)(void *)(audio_uart_mux_bitset+
                                           (uint8_t)group*8u+word*4u);
        if(*p!=0u) return 1u;
    }
    return 0u;
}
static void restore(uint32_t prior) {
    if(g2_log_is_privileged())
        __asm volatile("msr primask, %0" : : "r"(prior) : "memory");
}

uint32_t audio_uart_mux_on0(uint32_t pin) {
    if(audio_uart_mux_bit_get(0u,pin)==0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(0u,pin,1u);
        restore(prior);
    }
    return 0u;
}
uint32_t audio_uart_mux_off0(uint32_t pin) {
    if(audio_uart_mux_bit_get(0u,pin)!=0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(0u,pin,0u);
        restore(prior);
    }
    return 0u;
}
uint32_t audio_uart_mux_on1(uint32_t pin) {
    if(*(const volatile uint32_t *)(const void *)(audio_uart_mux_capabilities+12u)==0u)
        return 7u;
    if(audio_uart_mux_bit_get(1u,pin)==0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(1u,pin,1u);
        restore(prior);
    }
    return 0u;
}
uint32_t audio_uart_mux_off1(uint32_t pin) {
    if(audio_uart_mux_bit_get(1u,pin)!=0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(1u,pin,0u);
        restore(prior);
    }
    return 0u;
}

uint32_t audio_uart_mux_on3(uint32_t pin) { /* native 0x4c3cd4 */
    uint32_t config=audio_uart_mux_group3_active_pin;
    if(*(const volatile uint32_t *)(const void *)(audio_uart_mux_capabilities+16u)==0u)
        return 7u;
    if(audio_uart_mux_bit_get(3u,pin)==0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)g2_codec_pin_function(0xfu,(config&~15u)|10u);
        (void)audio_uart_mux_bit_set(3u,pin,1u);
        restore(prior);
    }
    return 0u;
}
uint32_t audio_uart_mux_off3(uint32_t pin) { /* native 0x4c3d28 */
    if(audio_uart_mux_bit_get(3u,pin)!=0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(3u,pin,0u);
        if(audio_uart_mux_any(3u)==0u)
            (void)g2_codec_pin_function(0xfu,audio_uart_mux_group3_idle_pin);
        restore(prior);
    }
    return 0u;
}

uint32_t audio_uart_mux_off4(uint32_t pin) { /* native 0x4c4016 */
    if(audio_uart_mux_bit_get(4u,pin)!=0u) {
        uint32_t prior=g2_gpio_critical_save();
        (void)audio_uart_mux_bit_set(4u,pin,0u);
        if(audio_uart_mux_any(4u)==0u)
            audio_uart_mux_group4_power(0u);
        restore(prior);
    }
    return 0u;
}

uint32_t audio_uart_mux_group4_power(uint32_t enabled) { /* native 0x4d391e */
    *audio_uart_mux_group4_power_word=(*audio_uart_mux_group4_power_word&~1u)|
                                      (enabled!=0u);
    return 0u;
}
