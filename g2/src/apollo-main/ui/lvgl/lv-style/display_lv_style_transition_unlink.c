/* Native transition deletion 0x450500 and node cleanup 0x450b0c.
 * Transition list 0x2006f5f4 is LV root 0x2006f548 plus 0xac. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[];
extern void *audio_uart_lv_list_first(void *); /* selected 0x482cd8 */
extern void *audio_uart_lv_list_next(void *,void *); /* selected 0x482cf0 */
extern void audio_uart_lv_list_remove_482c0e(void *,void *);
extern void audio_uart_lv_heap_free(void *); /* selected 0x44f758 */
extern void audio_uart_lv_transition_schedule_4509da(void);
void audio_uart_lv_transition_destroy_450b0c(void *node) {
    audio_uart_lv_list_remove_482c0e(audio_uart_display_lv_root+0xacu,node);
    uint8_t *n=(uint8_t *)node;
    void (*cleanup)(void *)=*(void (**)(void *))(void *)(n+0x14u);
    if(cleanup!=0)cleanup(node);
    audio_uart_lv_heap_free(node);
}
uint32_t audio_uart_lv_style_unlink_450500(void *object,void *style) {
    uint8_t removed=0u;
    void *list=audio_uart_display_lv_root+0xacu;
    for(uint32_t *node=(uint32_t *)audio_uart_lv_list_first(list);node!=0;) {
        if((object==0 || (void *)(uintptr_t)node[0]==object) &&
           (style==0 || (void *)(uintptr_t)node[1]==style)) {
            audio_uart_lv_transition_destroy_450b0c(node);
            audio_uart_lv_transition_schedule_4509da();
            removed=1u;
            node=(uint32_t *)audio_uart_lv_list_first(list);
        }
        else node=(uint32_t *)audio_uart_lv_list_next(list,node);
    }
    return removed;
}
