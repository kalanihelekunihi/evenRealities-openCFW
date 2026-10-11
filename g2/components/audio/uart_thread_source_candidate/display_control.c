/* Native display/DMA control at 0x471c9a, 0x471bca, 0x471dac,
 * and 0x471d58. Register base and format mask are product data. */
#include <stdbool.h>
#include <stdint.h>

extern volatile uint8_t *const audio_uart_display_engine_mmio; /* DAT_00471ed0 */
extern const uint32_t audio_uart_display_format_mask; /* DAT_00471ecc */
extern uint32_t g2_gpio_critical_save(void); /* selected 0x473940 */
extern bool g2_log_is_privileged(void); /* selected native privilege test */
extern uint32_t audio_uart_pin_mux_disable(uint32_t,uint32_t); /* 0x4c4530 */

static uint16_t read16(const uint8_t *p,uint32_t o) {
    return *(const uint16_t *)(const void *)(p+o);
}
static uint32_t read32(const uint8_t *p,uint32_t o) {
    return *(const uint32_t *)(const void *)(p+o);
}
static volatile uint32_t *channel_register(uint32_t channel,uint32_t offset) {
    return (volatile uint32_t *)(void *)(audio_uart_display_engine_mmio+
                                         0x200u+channel*0x20u+offset);
}

static uint32_t configure_channel(uint32_t channel,const uint8_t *p) {
    if(channel==14u || channel==15u) return 3u;
    uint32_t limit0=read32(p,16u),limit1=read32(p,20u);
    uint8_t mode=p[2];
    if(mode==1u) {
        if(limit1!=UINT32_MAX && limit0<=limit1) return 7u;
    } else if(mode!=2u && mode!=4u) {
        if((mode!=12u && mode!=13u) || read32(p,12u)>63u) return 7u;
    }
    volatile uint32_t *ctrl=channel_register(channel,0u);
    *ctrl &=~1u;
    *ctrl=(audio_uart_display_format_mask&
           ((uint32_t)(int32_t)(int16_t)read16(p,0u)<<8))|
          ((uint32_t)(p[2]&15u)<<4)|((uint32_t)p[4]<<3)|
          ((uint32_t)p[3]<<2)|((uint32_t)(p[5]&3u)<<17)|
          (read32(p,12u)<<24);
    *channel_register(channel,16u)=audio_uart_display_format_mask&
                       ((uint32_t)(int32_t)(int16_t)read16(p,6u)<<8);
    *channel_register(channel,8u)=limit0;
    *channel_register(channel,12u)=limit1;
    *ctrl |=2u;
    return 0u;
}

uint32_t audio_uart_display_control_apply(uint32_t channel,void *configuration) {
    return configure_channel(channel,(const uint8_t *)configuration);
}

static uint32_t pin_group(uint32_t pin) {
    if(pin<6u) return 4u;
    if(pin-6u<4u) return 0u;
    if(pin-19u<6u) return 5u;
    if(pin-25u<3u) return 2u;
    return 7u;
}

static void restore_if_privileged(uint32_t mask) {
    if(g2_log_is_privileged())
        __asm volatile("msr primask, %0" : : "r"(mask) : "memory");
}

static uint32_t display_channel_stop(uint32_t channel,bool pulse) {
    if(channel==14u || channel==15u) return 3u;
    volatile uint32_t *ctrl=channel_register(channel,0u);
    uint32_t pin=(*ctrl&0x1ffffu)>>8;
    uint32_t saved=g2_gpio_critical_save();
    *ctrl &=~1u;
    if(pulse) {
        *ctrl |=2u;
        *ctrl &=~2u;
    }
    restore_if_privileged(saved);
    if(pin<28u) (void)audio_uart_pin_mux_disable(pin_group(pin),
                                                 (channel+0x22u)&255u);
    return 0u;
}

uint32_t audio_uart_display_clock_select(uint32_t channel) {
    return display_channel_stop(channel,true);
}

uint32_t audio_uart_display_start(uint32_t channel) {
    return display_channel_stop(channel,false);
}
