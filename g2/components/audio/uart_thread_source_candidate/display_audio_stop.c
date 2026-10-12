/* Full native stop selector at 0x45faa8. The fourth incoming register is not
 * consumed by this routine; live descriptor ownership belongs to its caller. */
#include <stdint.h>
extern void audio_uart_display_audio_stop_all_45f6da(void *,uint32_t);
extern void *audio_uart_display_audio_find_45f840(void *,uint32_t);
extern void audio_uart_display_audio_stop_one_45f6c0(void *,uint32_t);
extern void audio_uart_display_audio_stop_top_45f6ec(void *,uint32_t);

uint32_t audio_uart_display_audio_stop(void *state,uint32_t mode,uint32_t id,uint32_t ambient)
{
    (void)ambient;
    if (state==0) return 0u;
    mode=(uint8_t)mode;
    if (mode==0u) {
        if (*(uint32_t *)state==0u) return 0u;
        audio_uart_display_audio_stop_all_45f6da(state,0u);
        return 1u;
    }
    if (mode>2u || id==0u) return 0u;
    uint8_t *entry=audio_uart_display_audio_find_45f840(state,id);
    if (entry==0 || entry[11u]!=1u) return 0u;
    if (mode==1u) {
        audio_uart_display_audio_stop_one_45f6c0(state,id);
        return 1u;
    }
    uint32_t *head=*(uint32_t **)state;
    if (head==0 || *head!=id) audio_uart_display_audio_stop_top_45f6ec(state,id);
    return 1u;
}
