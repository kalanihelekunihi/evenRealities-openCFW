/* Native display startup0x444694 and startup1 0x4446b4.
 * These are complete outer bodies with genuine lower imports. */
#include <stdint.h>

extern void audio_uart_display_clock_prepare(void); /* 0x473548 */
extern void audio_uart_display_board_config(const void *); /* 0x44d254 */
extern void audio_uart_display_clock_finish(void); /* 0x473928 */
extern const void *audio_uart_display_board_data; /* DAT_004448bc */

extern uint8_t audio_uart_display_control[]; /* DAT_004448c0, at least 24 bytes */
extern void audio_uart_display_control_reset(void *); /* 0x471cae */
extern uint32_t audio_uart_display_control_apply(uint32_t,void *); /* 0x471c9a */
extern uint32_t audio_uart_display_clock_select(uint32_t); /* 0x471dac */
extern void audio_uart_display_clock_gate(uint32_t); /* 0x471e92 */
extern void audio_uart_display_pin_config(uint32_t,uint32_t); /* 0x442256 */
extern void audio_uart_display_pin_enable(uint32_t); /* 0x442238 */
extern uint32_t g2_codec_global_irq_enable(void); /* selected exact 0x473934 */
extern uint32_t audio_uart_display_start(uint32_t); /* 0x471d58 */

/* Native MMIO and RAM children. Base addresses are product-owned data. */
extern volatile uint8_t *const audio_uart_display_board_mmio; /* DAT_0044d320 */
extern volatile uint32_t *const audio_uart_display_enable_word; /* DAT_00471edc */
extern volatile uint8_t *const audio_uart_display_pin_low; /* DAT_00442cd0 */
extern volatile uint8_t *const audio_uart_display_pin_high; /* DAT_00442ccc */
extern volatile uint32_t *const audio_uart_display_pin_set; /* DAT_00442cc8 */

void audio_uart_display_setup0(void) {
    audio_uart_display_clock_prepare();
    audio_uart_display_board_config(audio_uart_display_board_data);
    audio_uart_display_clock_finish();
}

void audio_uart_display_setup1(void) {
    uint8_t *state=audio_uart_display_control;
    audio_uart_display_control_reset(state);
    state[0]=1u;
    state[2]=2u;
    *(uint32_t *)(void *)(state+12u)=0u;
    *(uint32_t *)(void *)(state+16u)=6000u;
    (void)audio_uart_display_control_apply(0u,state);
    (void)audio_uart_display_clock_select(0u);
    audio_uart_display_clock_gate(1u);
    audio_uart_display_pin_config(0x43u,4u);
    audio_uart_display_pin_enable(0x43u);
    (void)g2_codec_global_irq_enable();
    (void)audio_uart_display_start(0u);
}

void audio_uart_display_board_config(const void *board) {
    *(volatile uint32_t *)(void *)(audio_uart_display_board_mmio+0x16cu)=
        (uint32_t)(uintptr_t)board;
}

void audio_uart_display_control_reset(void *control) {
    uint8_t *p=(uint8_t *)control;
    *(uint16_t *)(void *)p=1u;
    p[2]=1u;p[3]=0u;p[4]=0u;p[5]=0u;
    *(uint16_t *)(void *)(p+6u)=1u;
    *(uint32_t *)(void *)(p+12u)=0u;
    *(uint32_t *)(void *)(p+16u)=UINT32_MAX;
    *(uint32_t *)(void *)(p+20u)=UINT32_MAX;
}

void audio_uart_display_clock_gate(uint32_t mask) {
    *audio_uart_display_enable_word|=mask;
}

void audio_uart_display_pin_config(uint32_t pin,uint32_t mode) {
    if((int16_t)pin<0)
        audio_uart_display_pin_low[(int32_t)(pin&15u)-4]=(uint8_t)(mode<<4);
    else audio_uart_display_pin_high[pin]=(uint8_t)(mode<<4);
}

void audio_uart_display_pin_enable(uint32_t pin) {
    if((int16_t)pin>=0)
        audio_uart_display_pin_set[((uint32_t)(int16_t)pin)>>5]=1u<<(pin&31u);
}
