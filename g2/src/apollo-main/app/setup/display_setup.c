/* Native display startup0x444694 and startup1 0x4446b4.
 * These are complete outer bodies with genuine lower imports. */
#include <stdint.h>

extern void audio_uart_display_clock_prepare(void); /* 0x473548 */
extern void audio_uart_display_board_config(const void *); /* 0x44d254 */
extern void audio_uart_display_clock_finish(void); /* 0x473928 */
extern const void *audio_uart_display_board_data; /* DAT_004448bc */

extern uint8_t audio_uart_display_control[]; /* DAT_004448c0, at least 24 bytes */
/* AmbiqSuite 5.1.0 am_hal_timer.c (upstream unit), stock 0x471cae/0x471c9a/
 * 0x471dac/0x471e92/0x471d58. The config is am_hal_timer_config_t (24 bytes
 * with one-byte enums). */
extern uint32_t am_hal_timer_default_config_set(void *);
extern uint32_t am_hal_timer_config(uint32_t,void *);
extern uint32_t am_hal_timer_clear_stop(uint32_t);
extern uint32_t am_hal_timer_interrupt_enable(uint32_t);
extern void audio_uart_display_pin_config(uint32_t,uint32_t); /* 0x442256 */
extern void audio_uart_display_pin_enable(uint32_t); /* 0x442238 */
extern uint32_t g2_codec_global_irq_enable(void); /* selected exact 0x473934 */
extern uint32_t am_hal_timer_disable(uint32_t);

/* Native MMIO and RAM children. Base addresses are product-owned data. */
extern volatile uint8_t *const audio_uart_display_board_mmio; /* DAT_0044d320 */
extern volatile uint8_t *const audio_uart_display_pin_low; /* DAT_00442cd0 */
extern volatile uint8_t *const audio_uart_display_pin_high; /* DAT_00442ccc */
extern volatile uint32_t *const audio_uart_display_pin_set; /* DAT_00442cc8 */

/* Stock 0x444694 (display_thread.c LVGL startup) */
void audio_uart_display_setup0(void) {
    audio_uart_display_clock_prepare();
    audio_uart_display_board_config(audio_uart_display_board_data);
    audio_uart_display_clock_finish();
}

/* Stock 0x4446B4 (display_thread.c TIMER0 1 ms LVGL tick setup) */
void audio_uart_display_setup1(void) {
    uint8_t *state=audio_uart_display_control;
    (void)am_hal_timer_default_config_set(state);
    state[0]=1u;
    state[2]=2u;
    *(uint32_t *)(void *)(state+12u)=0u;
    *(uint32_t *)(void *)(state+16u)=6000u;
    (void)am_hal_timer_config(0u,state);
    (void)am_hal_timer_clear_stop(0u);
    (void)am_hal_timer_interrupt_enable(1u);
    audio_uart_display_pin_config(0x43u,4u);
    audio_uart_display_pin_enable(0x43u);
    (void)g2_codec_global_irq_enable();
    (void)am_hal_timer_disable(0u);
}

/* Retired: stock 0x44d254 is upstream lv_log_register_print_cb (lvgl/src/misc/lv_log.c); this name is a link alias. */
void audio_uart_display_board_config(const void *board);

/* Stock 0x442256 (__NVIC_SetPriority; upstream third-party/upstream/cmsis-5-590/CMSIS/Core/Include/core_cm55.h) */
void audio_uart_display_pin_config(uint32_t pin,uint32_t mode) {
    if((int16_t)pin<0)
        audio_uart_display_pin_low[(int32_t)(pin&15u)-4]=(uint8_t)(mode<<4);
    else audio_uart_display_pin_high[pin]=(uint8_t)(mode<<4);
}

/* Stock 0x442238 (__NVIC_EnableIRQ; upstream third-party/upstream/cmsis-5-590/CMSIS/Core/Include/core_cm55.h) */
void audio_uart_display_pin_enable(uint32_t pin) {
    if((int16_t)pin>=0)
        audio_uart_display_pin_set[((uint32_t)(int16_t)pin)>>5]=1u<<(pin&31u);
}
