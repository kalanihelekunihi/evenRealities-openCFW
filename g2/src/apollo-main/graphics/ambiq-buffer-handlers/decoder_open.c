/* Apollo LVGL image decoder open at 0x488f9c..0x48908b. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_image_memzero_488f40(void *,uint32_t);
extern uint32_t audio_uart_lv_image_source_type_488cb8(const void *);
extern uint32_t audio_uart_lv_image_cache_enabled_4d4b24(void);
extern uint32_t audio_uart_lv_decoder_cache_489460(void *);
extern uint32_t audio_uart_lv_decoder_find_48925a(void *,void *);
extern void audio_uart_lv_decoder_default_options_4d4ccc(void *,uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern void audio_uart_lv_draw_flush_cache_48abb8(void *,const void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char decoder_open_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_image_decoder.c";
static const char decoder_open_name[] = "lv_image_decoder_open";
static const char decoder_open_assert_message[] = "Asserted at expression: %s (%s)";
static const char decoder_open_assert_expression[] =
    "dsc->decoded->unaligned_data && dsc->decoded->handlers";
static const char decoder_open_assert_reason[] = "Invalid draw buffer";

uint32_t audio_uart_lv_image_decoder_open_488f9c(
        void *decoder_result,const void *source,const uint8_t *options,
        uint32_t reserved) {
    (void)reserved;
    uint8_t *out=(uint8_t *)decoder_result;
    audio_uart_lv_image_memzero_488f40(out,76u);
    if (source==0) return 0u;
    *(uint32_t *)(void *)(out+12u)=(uint32_t)(uintptr_t)source;
    out[16]=(uint8_t)audio_uart_lv_image_source_type_488cb8(source);
    if (audio_uart_lv_image_cache_enabled_4d4b24()!=0u) {
        *(uint32_t *)(void *)(out+64u)=
            *(uint32_t *)(void *)(audio_uart_display_lv_root+0x134u);
        if ((options==0 || options[2]==0u) &&
            (audio_uart_lv_decoder_cache_489460(out)&0xffu)==1u)
            return 1u;
    }
    const uint32_t decoder=audio_uart_lv_decoder_find_48925a(out,out+32u);
    *(uint32_t *)(void *)out=decoder;
    if (decoder==0u) return 0u;
    uint8_t defaults[8];
    if (options!=0)
        audio_queue_copy_bytes(defaults,options,5u);
    else
        audio_uart_lv_decoder_default_options_4d4ccc(defaults,5u);
    audio_queue_copy_bytes(out+4u,defaults,5u);
    const uint32_t callback=*(const uint32_t *)(uintptr_t)(decoder+4u);
    const uint32_t result=((uint32_t (*)(uint32_t,void *))(uintptr_t)callback)(
        decoder,out)&0xffu;
    if (result==1u && *(uint32_t *)(void *)(out+44u)!=0u) {
        const uint32_t decoded=*(uint32_t *)(void *)(out+44u);
        if (*(uint32_t *)(uintptr_t)(decoded+20u)==0u ||
            *(uint32_t *)(uintptr_t)(decoded+24u)==0u) {
            audio_uart_lvgl_log(3u,decoder_open_path,132u,decoder_open_name,
                                decoder_open_assert_message,
                                decoder_open_assert_expression,
                                decoder_open_assert_reason);
            for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
        }
        if (out[8]!=0u)
            audio_uart_lv_draw_flush_cache_48abb8((void *)(uintptr_t)decoded,0);
    }
    return result;
}
