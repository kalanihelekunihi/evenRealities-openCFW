/* lv_obj_send_event at native 0x451670, from pinned LVGL 9.3 source.
 * Stock leaves five bits of the flags storage byte from entry SP-16; the
 * target ABI bridge makes that byte explicit before the C body runs. */
#include <stdint.h>
typedef struct lv_event_native {
    void *current_target;
    void *original_target;
    uint32_t code;
    void *user_data;
    void *param;
    struct lv_event_native *prev;
    uint8_t deleted:1;
    uint8_t stop_processing:1;
    uint8_t stop_bubbling:1;
} lv_event_native;
extern void audio_uart_lv_event_scope_begin_44ffd0(void *);
extern void audio_uart_lv_event_scope_end_44ffdc(void *);
extern uint32_t audio_uart_lv_event_core_451a6c(void *);

uint32_t audio_uart_lv_obj_event_model_451670(void *object,uint32_t code,void *param,
                                                uint32_t entry_stack_byte) {
    if(object==0)return 1u;
    lv_event_native event;
    event.current_target=object;
    event.original_target=object;
    event.code=code;
    event.user_data=0;
    event.param=param;
    event.deleted=0;
    event.stop_bubbling=0;
    event.stop_processing=0;
    ((uint8_t *)(void *)&event)[24]=(uint8_t)(entry_stack_byte&0xf8u);
    audio_uart_lv_event_scope_begin_44ffd0(&event);
    uint32_t result=audio_uart_lv_event_core_451a6c(&event);
    audio_uart_lv_event_scope_end_44ffdc(&event);
    return (uint8_t)result;
}

/* Native prologue pushes 12 bytes then reserves 28; event.flags is at
 * new SP+24, which equals entry SP-16. Preserve that exact preexisting byte
 * before the C model establishes its own stack frame. */
__attribute__((naked)) uint32_t audio_uart_lv_obj_event_451670(void *object,uint32_t code,void *param) {
    __asm volatile("ldrb r3, [sp, #-16]\n b audio_uart_lv_obj_event_model_451670");
}
