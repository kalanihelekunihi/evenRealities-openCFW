/* Native TinyFrame TF_AddIdListener 0x4918c2, 128-entry ID-listener table. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* native 0x43d0ce */
extern void audio_log_extended(uint32_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char module[]="TinyFrame";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\TinyFrame\\TinyFrame.c";
static const char function[]="TF_AddIdListener";
static const char error_text[]="[TF] :error Failed to add ID listener\n";
static const char compact_text[]="[TinyFrame][TF] :error Failed to add ID listener\n";

uint32_t audio_uart_frame_extra(void *frame_state,const void *frame,
                                 uint32_t handler,uint32_t context,uint16_t sequence)
{
    uint8_t *const state=(uint8_t *)frame_state;
    const uint8_t *const src=(const uint8_t *)frame;
    for (unsigned slot=0;slot<128u;++slot) {
        uint8_t *entry=state+0x6430u+slot*24u;
        if (*(uint32_t *)(void *)(entry+4u)!=0u) continue;
        *(uint32_t *)(void *)(entry+4u)=handler;
        *(uint32_t *)(void *)(entry+8u)=context;
        *(uint16_t *)(void *)entry=*(const uint16_t *)(const void *)src;
        *(uint32_t *)(void *)(entry+16u)=*(const uint32_t *)(const void *)(src+16u);
        *(uint32_t *)(void *)(entry+20u)=*(const uint32_t *)(const void *)(src+20u);
        *(uint16_t *)(void *)(entry+12u)=sequence;
        *(uint16_t *)(void *)(entry+14u)=*(const uint16_t *)(const void *)(entry+12u);
        if (state[0x7158u] <= slot) state[0x7158u]=(uint8_t)(slot+1u);
        return 1u;
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,source,function,0x14cu,error_text);
    if ((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,compact_text,compact_text);
    return 0u;
}
