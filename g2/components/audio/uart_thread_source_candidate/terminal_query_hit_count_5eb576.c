/* Query overlapping-child counter, stock 0x5eb576..0x5eb61d. */
#include <stdint.h>

extern uint8_t audio_terminal_ui_state_base[0x2a0];
extern int32_t audio_terminal_query_height_5eb438(uint8_t *);
extern int32_t audio_uart_lv_obj_y_43fce0(void *);
extern uint32_t audio_terminal_query_count_5eb30c(void);
extern void *audio_lv_child_44dce2(void *,uint32_t);
extern int32_t audio_uart_lv_obj_height_43fdda(void *);

static uint32_t word(uint32_t offset) {
    const uint8_t *p=audio_terminal_ui_state_base+offset;
    return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
           ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);
}

uint32_t audio_terminal_query_hit_count_5eb576(uint32_t threshold,int32_t y) {
    uint32_t root=word(0x214u),list=word(0x21cu);
    if (root==0u || list==0u || (uint8_t)threshold==0u) return 0u;
    int32_t end=audio_terminal_query_height_5eb438(audio_terminal_ui_state_base)+y;
    int32_t parent_y=audio_uart_lv_obj_y_43fce0((void *)(uintptr_t)list);
    uint8_t count=(uint8_t)audio_terminal_query_count_5eb30c();
    uint32_t hits=0u;
    for (uint32_t i=0u;(uint8_t)i<count;++i) {
        void *child=audio_lv_child_44dce2((void *)(uintptr_t)list,(uint8_t)i);
        if (child==0) continue;
        int32_t top=audio_uart_lv_obj_y_43fce0(child)+parent_y;
        int32_t bottom=audio_uart_lv_obj_height_43fdda(child)+top;
        if (y<bottom && top<end) {
            ++hits;
            if ((uint8_t)hits>=(uint8_t)threshold) return 1u;
        }
    }
    return 0u;
}
