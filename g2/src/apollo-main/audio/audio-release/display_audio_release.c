/* Native display audio/page release 0x45f7be. */
#include <stdint.h>

extern uint32_t audio_uart_lv_style_unlink_450500(void *,void *); /* selected 0x450500 */
extern void audio_uart_display_event_remove_callback(void *,void (*)(void)); /* 0x451862 */
extern void audio_uart_page_event_45f914(void); /* Thumb callback 0x45f915 */
extern void audio_uart_display_page_deinit(void *); /* 0x45fbae */
extern void audio_uart_display_object_delete(void *); /* 0x44d7b8 */
extern void audio_file_heap_free(void *); /* selected 0x474d16 */
extern void audio_uart_display_audio_finalize(void); /* 0x45bbd2 */

static uint32_t read_word(const uint8_t *p,unsigned offset)
{
    return *(const uint32_t *)(const void *)(p+offset);
}

void audio_uart_display_audio_release(uint32_t address)
{
    if (address==0u) return;
    uint8_t *const state=(uint8_t *)(uintptr_t)address;
    for (unsigned list=0;list<2u;++list) {
        uint32_t node=read_word(state,8u+list*4u);
        while (node!=0u) {
            uint8_t *const entry=(uint8_t *)(uintptr_t)node;
            (void)audio_uart_lv_style_unlink_450500((void *)(uintptr_t)read_word(entry,4u),0);
            node=read_word(entry,32u);
        }
    }
    audio_uart_display_event_remove_callback((void *)(uintptr_t)read_word(state,24u),
                                               audio_uart_page_event_45f914);
    audio_uart_display_page_deinit(state+36u);
    state[232u]=0u;
    *(uint32_t *)(void *)(state+0u)=0u;
    *(uint32_t *)(void *)(state+4u)=0u;
    *(uint32_t *)(void *)(state+16u)=0u;
    audio_uart_display_object_delete((void *)(uintptr_t)read_word(state,24u));
    for (unsigned list=0;list<2u;++list) {
        uint32_t node=read_word(state,8u+list*4u);
        while (node!=0u) {
            uint8_t *const entry=(uint8_t *)(uintptr_t)node;
            uint32_t next=read_word(entry,32u);
            audio_file_heap_free(entry);
            node=next;
        }
    }
    audio_file_heap_free(state);
    audio_uart_display_audio_finalize();
}
