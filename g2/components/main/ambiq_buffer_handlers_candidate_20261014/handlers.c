/* Apollo S200 Ambiq buffer callback table at 0x53d5da. */
#include <stdint.h>

extern uint32_t audio_uart_ambiq_buffer_base_53cf78(uint32_t,uint32_t,
                                                      uint32_t);
extern uint32_t audio_uart_ambiq_buffer_update_53cf8a(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_buffer_mask_53d006(uint32_t,uint32_t,
                                                      uint32_t);
extern uint32_t audio_uart_ambiq_buffer_layout_53d062(uint32_t,uint32_t,
                                                        uint32_t);
extern uint32_t audio_uart_ambiq_buffer_round_bytes_53cfe4(uint32_t);
extern uint32_t audio_uart_ambiq_buffer_format_bytes_53cff0(uint32_t,
                                                               uint32_t);
extern uint32_t audio_uart_ambiq_buffer_blend_53d0b6(uint32_t,uint32_t);
extern uint32_t audio_uart_ambiq_buffer_render_53d25a(uint32_t,uint32_t);

void audio_uart_ambiq_buffer_call_base_53d56a(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_base_53cf78(1u,a,b & 0xffu);
}
void audio_uart_ambiq_buffer_call_update_53d57a(uint32_t a) {
    (void)audio_uart_ambiq_buffer_update_53cf8a(1u,a);
}
void audio_uart_ambiq_buffer_call_mask_53d586(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_mask_53d006(1u,a,b);
}
void audio_uart_ambiq_buffer_call_layout_53d594(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_layout_53d062(1u,a,b);
}
void audio_uart_ambiq_buffer_call_base2_53d5a2(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_base_53cf78(1u,a,b & 0xffu);
}
void audio_uart_ambiq_buffer_call_update2_53d5b2(uint32_t a) {
    (void)audio_uart_ambiq_buffer_update_53cf8a(1u,a);
}
void audio_uart_ambiq_buffer_call_mask2_53d5be(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_mask_53d006(1u,a,b);
}
void audio_uart_ambiq_buffer_call_layout2_53d5cc(uint32_t a,uint32_t b) {
    (void)audio_uart_ambiq_buffer_layout_53d062(1u,a,b);
}

void audio_uart_ambiq_buffer_handlers_53d5da(void) {
    volatile uint32_t *const state =
        (volatile uint32_t *)(uintptr_t)0x2006f548u;
    state[0xc8u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_base_53d56a;
    state[0xccu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_update_53d57a;
    state[0xd8u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_mask_53d586;
    state[0xd4u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_layout_53d594;
    state[0xd0u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_round_bytes_53cfe4;
    state[0xdcu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_format_bytes_53cff0;
    state[0xe0u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_blend_53d0b6;
    state[0xe4u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_render_53d25a;
    state[0x108u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_base2_53d5a2;
    state[0x10cu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_update2_53d5b2;
    state[0x118u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_mask2_53d5be;
    state[0x114u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_layout2_53d5cc;
    state[0x110u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_round_bytes_53cfe4;
    state[0x11cu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_format_bytes_53cff0;
    state[0x120u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_blend_53d0b6;
    state[0x124u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_render_53d25a;
    state[0xe8u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_base2_53d5a2;
    state[0xecu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_update2_53d5b2;
    state[0xf8u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_mask2_53d5be;
    state[0xf4u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_call_layout2_53d5cc;
    state[0xf0u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_round_bytes_53cfe4;
    state[0xfcu/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_format_bytes_53cff0;
    state[0x100u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_blend_53d0b6;
    state[0x104u/4u] = (uint32_t)(uintptr_t)
        audio_uart_ambiq_buffer_render_53d25a;
}
