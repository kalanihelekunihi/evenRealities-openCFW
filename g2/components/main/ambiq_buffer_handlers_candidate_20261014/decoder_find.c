/* Apollo LVGL image decoder selection at 0x48925a..0x4893e5. */
#include <stdint.h>

extern uint8_t audio_uart_display_lv_root[];
extern void audio_uart_lv_image_memzero_488f40(void *,uint32_t);
extern uint32_t audio_uart_lv_cache_enabled_4d5104(void *);
extern uint32_t audio_uart_lv_cache_lookup_4d4dca(uint32_t,const void *,uint32_t);
extern uint32_t audio_uart_lv_cache_entry_4d5396(uint32_t);
extern void audio_uart_lv_decoder_release_4d4e72(uint32_t,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_open_4c6d9a(void *,const void *,uint32_t);
extern uint32_t audio_uart_lv_fs_file_seek_4c6fba(void *,uint32_t,uint32_t);
extern uint32_t audio_uart_lv_fs_file_close_4c6ee0(void *);
extern void *audio_uart_lv_list_first(void *);
extern void *audio_uart_lv_list_next(void *,void *);
extern uint32_t audio_uart_lv_color_bpp_440f44(uint32_t);
extern char *audio_uart_font_path_duplicate(const char *);
extern uint32_t audio_uart_lv_cache_add_4d4eea(uint32_t,const void *,uint32_t);
extern void audio_uart_lv_free(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char decoder_find_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\lv_image_decoder.c";
static const char decoder_find_name[] = "image_decoder_get_info";
static const char decoder_find_open_error[] = "File open failed: %u";

uint32_t audio_uart_lv_image_header_cache_enabled_4d4c2c(void) {
    uint32_t cache=*(uint32_t *)(void *)(audio_uart_display_lv_root+0x138u);
    return audio_uart_lv_cache_enabled_4d5104((void *)(uintptr_t)cache);
}

uint32_t audio_uart_lv_image_decoder_stride_4893e6(const void *header) {
    const uint32_t *h=(const uint32_t *)header;
    const uint32_t cf=(h[0]>>8)&0xffu;
    if (cf==20u) return (h[1]<<1)&0x1fffeu;
    const uint32_t bpp=audio_uart_lv_color_bpp_440f44(cf)&0xffu;
    return (bpp*(h[1]&0xffffu)+7u)>>3u;
}

uint32_t audio_uart_lv_decoder_find_48925a(void *decoder_result,void *metadata) {
    uint8_t *out=(uint8_t *)decoder_result;
    uint32_t *header=(uint32_t *)metadata;
    audio_uart_lv_image_memzero_488f40(header,12u);
    const uint32_t source=*(uint32_t *)(void *)(out+12u);
    const uint32_t kind=out[16u];
    if (kind==0u && *(uint32_t *)(uintptr_t)(source+16u)==0u) return 0u;
    const uint32_t header_cache_active=
        audio_uart_lv_image_header_cache_enabled_4d4c2c()&0xffu;
    const uint32_t header_cache=
        *(uint32_t *)(void *)(audio_uart_display_lv_root+0x138u);
    if (header_cache_active!=0u && kind==1u) {
        uint32_t key[2]={source,1u};
        const uint32_t entry=audio_uart_lv_cache_lookup_4d4dca(
            header_cache,key,0u);
        if (entry!=0u) {
            const uint32_t data=audio_uart_lv_cache_entry_4d5396(entry);
            const uint32_t *cached=(const uint32_t *)(uintptr_t)(data+8u);
            header[0]=cached[0];header[1]=cached[1];header[2]=cached[2];
            const uint32_t decoder=*(uint32_t *)(uintptr_t)(data+20u);
            audio_uart_lv_decoder_release_4d4e72(header_cache,entry,0u);
            return decoder;
        }
    }
    if (kind==1u) {
        const uint32_t opened=audio_uart_lv_fs_file_open_4c6d9a(
            out+20u,(const void *)(uintptr_t)source,2u)&0xffu;
        if (opened!=0u) {
            audio_uart_lvgl_log(3u,decoder_find_path,336u,decoder_find_name,
                                decoder_find_open_error,opened);
            return 0u;
        }
    }
    uint32_t decoder=(uint32_t)(uintptr_t)audio_uart_lv_list_first(
        audio_uart_display_lv_root+0x128u);
    while (decoder!=0u) {
        const uint32_t info=*(uint32_t *)(uintptr_t)decoder;
        const uint32_t open=*(uint32_t *)(uintptr_t)(decoder+4u);
        if (info!=0u && open!=0u) {
            (void)audio_uart_lv_fs_file_seek_4c6fba(out+20u,0u,0u);
            const uint32_t status=((uint32_t (*)(uint32_t,void *,void *))
                (uintptr_t)info)(decoder,decoder_result,metadata)&0xffu;
            if (status==1u) {
                if ((header[2]&0xffffu)==0u) {
                    const uint32_t stride=
                        audio_uart_lv_image_decoder_stride_4893e6(header);
                    header[2]=(header[2]&0xffff0000u)|(stride&0xffffu);
                }
                break;
            }
        }
        decoder=(uint32_t)(uintptr_t)audio_uart_lv_list_next(
            audio_uart_display_lv_root+0x128u,(void *)(uintptr_t)decoder);
    }
    if (kind==1u) (void)audio_uart_lv_fs_file_close_4c6ee0(out+20u);
    if (header_cache_active!=0u && kind==1u && decoder!=0u) {
        uint32_t key[6];
        key[0]=(uint32_t)(uintptr_t)audio_uart_font_path_duplicate(
            (const char *)(uintptr_t)source);
        key[1]=1u;
        key[2]=header[0];key[3]=header[1];key[4]=header[2];
        key[5]=decoder;
        const uint32_t entry=audio_uart_lv_cache_add_4d4eea(
            header_cache,key,0u);
        if (entry==0u) {
            audio_uart_lv_free((void *)(uintptr_t)key[0]);
            return 0u;
        }
        audio_uart_lv_decoder_release_4d4e72(header_cache,entry,0u);
    }
    return decoder;
}
