/* Full native lv_init outer body 0x473548, pinned LVGL v9.3 call order.
 * All nested system/font/display providers remain genuine source children. */
#include <stdint.h>
extern uint8_t audio_uart_display_lv_root[]; /* selected RAM0x2006f548 */
extern uint8_t audio_file_lfs_context[]; /* selected RAM0x20071ac8 */
extern void audio_uart_lv_init_global_4734cc(volatile uint8_t *);
extern void audio_uart_lv_init_memory_48aa60(void);
extern void audio_uart_lv_span_stack_init_4c6d04(void);
extern void audio_uart_lv_init_async_49acb0(void);
extern void audio_uart_lv_init_display_464330(void);
extern void audio_uart_lv_init_indev_4c6d8c(void);
extern void audio_uart_lv_init_theme_4546dc(void);
extern void audio_uart_lv_init_event_4503a4(void);
extern void audio_uart_lv_init_style_44d32c(void);
extern uint32_t audio_uart_lv_init_draw_unit_4b1b98(uint32_t);
extern void audio_uart_lv_init_anim_48438c(void);
extern void audio_uart_lv_init_group_4c73d6(void);
extern void audio_uart_lv_init_cache_44b90c(void);
extern void audio_uart_lv_image_decoder_init_488f4c(uint32_t,uint32_t);
extern void audio_uart_lv_bin_decoder_init_4c794c(void);
extern void audio_uart_lv_init_misc_4c8f0a(void);
extern void audio_uart_lv_init_global_bind_4c8efc(void *);
extern void audio_uart_lv_init_assert_4c91a8(void);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,...);

static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\lv_init.c";
static const char function[]="lv_init";
static const char already[]="lv_init: already initialized";
static const char bad_encoding[]="The strings have no UTF-8 encoding. Non-ASCII characters won't be displayed.";
static const char endian_text[]="It's a big endian system but LV_BIG_ENDIAN_SYSTEM is not enabled in lv_conf.h";
static const char endian_expression[]="LV_BIG_ENDIAN_SYSTEM == 1";
static const char assert_format[]="Asserted at expression: %s (%s)";
/* The native ADR at 0x4735b0 points to these three source version bytes. */
static const uint8_t version_bytes[3]={0xc3u,0x81u,0x00u};

/* Stock 0x473548 (FUN_00473548) */
void audio_uart_display_clock_prepare(void)
{
    if (audio_uart_display_lv_root[0]!=0u) {
        audio_uart_lvgl_log(2u,source,0xb9u,function,already);
        return;
    }
    audio_uart_lv_init_global_4734cc(audio_uart_display_lv_root);
    audio_uart_lv_init_memory_48aa60();
    audio_uart_lv_span_stack_init_4c6d04();
    audio_uart_lv_init_async_49acb0();
    audio_uart_lv_init_display_464330();
    audio_uart_lv_init_indev_4c6d8c();
    audio_uart_lv_init_theme_4546dc();
    audio_uart_lv_init_event_4503a4();
    audio_uart_lv_init_style_44d32c();
    audio_uart_lv_init_draw_unit_4b1b98(64u);
    audio_uart_lv_init_anim_48438c();
    audio_uart_lv_init_group_4c73d6();
    audio_uart_lv_init_cache_44b90c();
    audio_uart_lv_image_decoder_init_488f4c(0u,0u);
    audio_uart_lv_bin_decoder_init_4c794c();
    if (version_bytes[0]!=0xc3u || version_bytes[1]!=0x81u || version_bytes[2]!=0u)
        audio_uart_lvgl_log(2u,source,0x12cu,function,bad_encoding);
    const uint32_t endian_probe=0x11223344u;
    if (*(const uint8_t *)(const void *)&endian_probe==0x11u) {
        audio_uart_lvgl_log(3u,source,0x135u,function,
                            assert_format,endian_expression,endian_text);
        for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0u;
    }
    audio_uart_lv_init_misc_4c8f0a();
    audio_uart_lv_init_global_bind_4c8efc(audio_file_lfs_context);
    audio_uart_lv_init_assert_4c91a8();
    audio_uart_display_lv_root[0]=1u;
}
