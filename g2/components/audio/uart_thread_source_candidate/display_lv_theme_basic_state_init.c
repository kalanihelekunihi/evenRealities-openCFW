/* Native LV grid calc construction 0x48cad8, 32-byte state ABI. */
#include <stdint.h>
extern void *audio_uart_lv_child_get_44dce2(void *,int32_t);
extern void audio_uart_lv_basic_box_init_48c80e(void *,uint32_t);
extern void audio_uart_lv_basic_prepare_a_48cdec(void *,void *);
extern void audio_uart_lv_basic_prepare_b_48cbf8(void *,void *);
extern uint32_t audio_uart_lv_basic_horizontal_48c860(void *,uint32_t);
extern uint32_t audio_uart_lv_basic_vertical_48c856(void *,uint32_t);
extern uint8_t audio_uart_lv_grid_base_dir_48c8a8(void *,uint32_t);
extern int32_t audio_uart_lv_basic_width_48c81a(void *,uint32_t);
extern int32_t audio_uart_lv_basic_height_48c824(void *,uint32_t);
extern uint32_t audio_uart_lv_obj_content_width_43fe16(void *);
extern uint32_t audio_uart_lv_obj_content_height_43fe70(void *);
extern uint8_t audio_uart_lv_basic_h_mode_48c9cc(void *);
extern uint8_t audio_uart_lv_basic_v_mode_48c9d6(void *);
extern uint32_t audio_uart_lv_basic_axis_48d3c8(uint32_t,uint32_t,uint32_t,uint32_t,
                                                  uint32_t,uint32_t,uint32_t,uint32_t);

void audio_uart_lv_basic_state_init_48cad8(void *object,void *raw_state)
{
    uint32_t *state=(uint32_t *)raw_state;
    void *first_child=audio_uart_lv_child_get_44dce2(object,0);
    if(first_child==0) {
        audio_uart_lv_basic_box_init_48c80e(state,0x20u);
        return;
    }
    audio_uart_lv_basic_prepare_a_48cdec(object,state);
    audio_uart_lv_basic_prepare_b_48cbf8(object,state);
    uint32_t horizontal=audio_uart_lv_basic_horizontal_48c860(object,0u);
    uint32_t vertical=audio_uart_lv_basic_vertical_48c856(object,0u);
    uint32_t pad=audio_uart_lv_grid_base_dir_48c8a8(object,0u);
    int32_t width=audio_uart_lv_basic_width_48c81a(object,0u);
    int32_t height=audio_uart_lv_basic_height_48c824(object,0u);
    uint16_t flags=*(uint16_t *)(void *)((uint8_t *)object+0x2au);
    uint32_t h_auto=(width==0x3fffffff) ? (((flags&0xfffu)>>11)^1u) : 0u;
    state[6]=audio_uart_lv_basic_axis_48d3c8(
        audio_uart_lv_obj_content_width_43fe16(object),h_auto,
        audio_uart_lv_basic_h_mode_48c9cc(object),horizontal,
        state[4],state[2],state[0],pad==1u);
    uint32_t v_auto=(height==0x3fffffff) ? (((flags&0x7ffu)>>10)^1u) : 0u;
    state[7]=audio_uart_lv_basic_axis_48d3c8(
        audio_uart_lv_obj_content_height_43fe70(object),v_auto,
        audio_uart_lv_basic_v_mode_48c9d6(object),vertical,
        state[5],state[3],state[1],0u);
}
