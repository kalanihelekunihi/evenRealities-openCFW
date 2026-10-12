/* Native event-array compaction 0x4502e0/0x450346 and clear 0x488478.
 * The resize lower remains an explicit LV array allocator operation. */
#include <stdint.h>
extern uint32_t audio_uart_lv_event_count_450388(void *);
extern void *audio_uart_lv_event_slot_450390(void *,uint32_t);
extern uint32_t audio_uart_lv_event_descriptor_invalid_45037e(void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void *audio_uart_lv_realloc_44f76a(void *,uint32_t);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\lv_array.c";
__attribute__((noinline)) uint32_t audio_uart_lv_array_resize_48849c(void *array,uint32_t wanted) {
    uint8_t *a=(uint8_t *)array;
    if(a[0x10u]==0u) {
        audio_uart_lvgl_log(2u,path,0x8cu,"lv_array_resize",
                            "Cannot resize array with external buffer");
        return 0u;
    }
    uint32_t stride=*(uint32_t *)(void *)(a+0x0cu);
    void *new_data=audio_uart_lv_realloc_44f76a(*(void **)(void *)a,stride*wanted);
    if(new_data==0) {
        audio_uart_lvgl_log(3u,path,0x91u,"lv_array_resize",
                            "Asserted at expression: %s (%s)","data != NULL","NULL pointer");
        for(;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    *(void **)(void *)a=new_data;
    *(uint32_t *)(void *)(a+8u)=wanted;
    uint32_t count=*(uint32_t *)(void *)(a+4u);
    if(wanted<count)*(uint32_t *)(void *)(a+4u)=wanted;
    return 1u;
}
void audio_uart_lv_array_clear_488478(void *array) {
    uint8_t *a=(uint8_t *)array;
    void *data=*(void **)(void *)a;
    if(data!=0) {
        if(a[0x10u]!=0u)audio_uart_lv_heap_free(data);
        *(uint32_t *)(void *)a=0u;
    }
    *(uint32_t *)(void *)(a+4u)=0u;
    *(uint32_t *)(void *)(a+8u)=0u;
}
void audio_uart_lv_event_restore_4502e0(void *list) {
    uint32_t count=audio_uart_lv_event_count_450388(list);
    uint32_t kept=0u;
    for(uint32_t i=0;i<count;i++) {
        void *source=audio_uart_lv_event_slot_450390(list,i);
        void *destination=audio_uart_lv_event_slot_450390(list,kept);
        void *descriptor=*(void **)(void *)source;
        if(audio_uart_lv_event_descriptor_invalid_45037e(descriptor)==0u) {
            *(void **)(void *)destination=descriptor;
            kept++;
        }
        else audio_uart_lv_heap_free(descriptor);
    }
    if(kept==0u)audio_uart_lv_array_clear_488478(list);
    else (void)audio_uart_lv_array_resize_48849c(list,kept);
}
void audio_uart_lv_event_compact_450346(void *list) {
    uint8_t *flags=(uint8_t *)list+0x14u;
    if((*flags&1u)==0u && (*flags&2u)!=0u) {
        audio_uart_lv_event_restore_4502e0(list);
        *flags&=(uint8_t)~2u;
    }
}
