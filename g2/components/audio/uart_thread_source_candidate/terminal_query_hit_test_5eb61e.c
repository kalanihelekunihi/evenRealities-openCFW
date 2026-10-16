/* Terminal query hit-test facade, stock 0x5eb61e..0x5eb645. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern int32_t audio_uart_lv_obj_y_44e498(void *);
extern uint32_t audio_terminal_query_hit_count_5eb576(uint32_t,int32_t);

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_query_hit_test_5eb61e(uint32_t target) {
    uint32_t root=word(0x214u);
    if (root==0u) return 0u;
    int32_t y=audio_uart_lv_obj_y_44e498((void *)(uintptr_t)root);
    return audio_terminal_query_hit_count_5eb576((uint8_t)target,y);
}
