/* Native 0x46d238: cached 32-byte font glyph descriptor cache callback. */
#include <stdint.h>
extern uint8_t audio_uart_ring_config_idle; /* RAM0x20074fe3, cache gate */
extern uint8_t audio_uart_ring_config_workspace[]; /* RAM0x20324600, 512*40-byte entries */
extern uint32_t audio_uart_font_glyph_descriptor(void *,void *,uint32_t,uint32_t); /* 0x4b26a4 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439c04 equivalent */
uint32_t audio_uart_font_glyph_cache_callback(void *device,void *destination,
                                               uint32_t codepoint,uint32_t previous_codepoint) {
    if(audio_uart_ring_config_idle==0u||codepoint==0u)
        return audio_uart_font_glyph_descriptor(device,destination,codepoint,
                                                 previous_codepoint);
    uint32_t index=codepoint&0x1ffu;
    uint8_t *entry=audio_uart_ring_config_workspace+index*40u;
    if(*(const uint32_t *)(const void *)entry==codepoint) {
        (void)audio_queue_copy_bytes(destination,entry+8u,32u);
        return entry[4u];
    }
    uint32_t status=audio_uart_font_glyph_descriptor(device,destination,codepoint,
                                                      previous_codepoint);
    *(uint32_t *)(void *)entry=codepoint;
    (void)audio_queue_copy_bytes(entry+8u,destination,32u);
    entry[4u]=(uint8_t)status;
    return (uint8_t)status;
}
