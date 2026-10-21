/* Stock terminal UI cleanup children at 0x5ec268, 0x5ebbc6 and 0x5ec770. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0]; /* stock 0x2006e0d0 */
extern void *audio_uart_lv_obj_parent_44dca2(void *);
extern void audio_uart_page_delete_event_filter_44d7b8(void *);
extern uint32_t audio_td_counter_b_get(void);
extern void audio_terminal_ui_event_5e5484(uint32_t, uint32_t, uint32_t);
extern void audio_uart_display_audio_reset_441488(uint32_t, uint32_t, uint32_t);

static uint32_t load32(uint32_t offset) {
    return *(uint32_t *)(void *)(audio_terminal_ui_state_base + offset);
}

static void store32(uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(audio_terminal_ui_state_base + offset) = value;
}

static void stop_service(uint32_t offset, uint32_t count, uint32_t clear_byte) {
    uint32_t object = load32(offset);
    if (object != 0u) {
        void *parent = audio_uart_lv_obj_parent_44dca2((void *)(uintptr_t)object);
        audio_uart_page_delete_event_filter_44d7b8(
            parent != 0 ? parent : (void *)(uintptr_t)object);
        for (uint32_t index = 0; index < count; ++index)
            store32(offset + index * 4u, 0u);
        if (clear_byte != 0u)
            audio_terminal_ui_state_base[0x27cu] = 0u;
        audio_terminal_ui_event_5e5484(4u, audio_td_counter_b_get(), 0u);
    }
    object = load32(0u);
    if (object != 0u)
        audio_uart_display_audio_reset_441488(object, 0xffu, 0u);
}

void audio_terminal_ui_stop_service_b_5ec268(void) {
    stop_service(0x1f4u, 8u, 0u);
}

void audio_terminal_ui_stop_service_c_5ebbc6(void) {
    stop_service(0x214u, 4u, 1u);
}

void audio_terminal_ui_stop_service_d_5ec770(void) {
    stop_service(0x230u, 4u, 0u);
}
