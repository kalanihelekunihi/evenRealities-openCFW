/* Apollo Main input cleanup 0x452f26..0x452f5d and per-device cleanup
 * 0x45305c..0x4530f5. Both use the LVGL RAM state at 0x2006f548. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_state[];
extern void *audio_uart_lv_input_next_452edc(void *);
extern uint32_t audio_uart_lv_obj_event_451670(void *, uint32_t, void *);
extern uint32_t audio_uart_lv_input_event_453002(void *, uint32_t, void *);

static uint32_t get32(const uint8_t *bytes, uint32_t offset) {
    return *(const uint32_t *)(const void *)(bytes + offset);
}
static void put32(uint8_t *bytes, uint32_t offset, uint32_t value) {
    *(uint32_t *)(void *)(bytes + offset) = value;
}

void audio_uart_lv_input_cleanup_one_45305c(void *input, void *object) {
    uint8_t *const item = (uint8_t *)input;
    item[0x0bu] = (uint8_t)(item[0x0bu] | 2u);
    if (get32(audio_uart_display_lv_state, 0x50u) == (uint32_t)(uintptr_t)input)
        put32(audio_uart_display_lv_state, 0x54u, 0u);
    if (item[0] == 1u || item[0] == 2u) {
        if (object == 0 || get32(item, 0x74u) == (uint32_t)(uintptr_t)object)
            put32(item, 0x74u, 0u);
        uint32_t target = get32(item, 0x68u);
        if (target != 0u) {
            put32(item, 0x68u, 0u);
            (void)audio_uart_lv_obj_event_451670((void *)(uintptr_t)target, 0x17u, input);
            (void)audio_uart_lv_input_event_453002(input, 0x17u, (void *)(uintptr_t)target);
        }
        if (object == 0 || get32(item, 0x6cu) == (uint32_t)(uintptr_t)object)
            put32(item, 0x6cu, 0u);
        target = get32(item, 0x70u);
        if (target != 0u) {
            put32(item, 0x70u, 0u);
            (void)audio_uart_lv_obj_event_451670((void *)(uintptr_t)target, 0x17u, input);
            (void)audio_uart_lv_input_event_453002(input, 0x17u, (void *)(uintptr_t)target);
        }
        if (object == 0 || get32(item, 0x78u) == (uint32_t)(uintptr_t)object)
            put32(item, 0x78u, 0u);
    }
}

void audio_uart_lv_input_clear_452f26(void *input, void *object) {
    if (input == 0) {
        for (void *next = audio_uart_lv_input_next_452edc(0); next != 0;
             next = audio_uart_lv_input_next_452edc(next))
            audio_uart_lv_input_cleanup_one_45305c(next, object);
        put32(audio_uart_display_lv_state, 0x54u, 0u);
    } else {
        audio_uart_lv_input_cleanup_one_45305c(input, object);
    }
}
