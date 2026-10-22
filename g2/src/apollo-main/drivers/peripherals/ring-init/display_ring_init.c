/* Native 0x46d464: two ring lists and their published first elements. */
#include <stdint.h>
extern void audio_uart_display_ring_static_init(void); /* 0x46d29a */
extern void *audio_uart_display_ring_construct(const uint8_t *,uint32_t); /* 0x46cae0 */
extern void *audio_uart_display_ring_head(const uint32_t *); /* 0x46cf56 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint32_t audio_uart_ring_primary_list_cell; /* RAM0x200746d4 via DAT_0046d648 */
extern uint32_t audio_uart_ring_primary_head_cell; /* RAM0x200746dc via DAT_0046d650 */
extern uint32_t audio_uart_ring_secondary_list_cell; /* RAM0x200746d8 via DAT_0046d660 */
extern uint32_t audio_uart_ring_secondary_head_cell; /* RAM0x200746e0 via DAT_0046d668 */
extern const uint8_t audio_uart_ring_primary_descriptors[]; /* RAM0x20002c48 via DAT_0046d64c */
extern const uint8_t audio_uart_ring_secondary_descriptors[]; /* RAM0x20002c78 via DAT_0046d664 */
static const char audio_uart_ring_init_module[]="font_manager"; /* ROM0x00787a50 */
static const char audio_uart_ring_init_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\lvgl_font_manager.c"; /* ROM0x006fb45c */
static const char audio_uart_ring_init_function[]="font_manager_init"; /* ROM0x00781228 */
static const char audio_uart_ring_init_primary_error[]="Failed to create background font manager"; /* ROM0x0073fd94 */
static const char audio_uart_ring_init_primary_short[]="[font_manager]Failed to create background font manager"; /* ROM0x007202b8 */
static const char audio_uart_ring_init_secondary_error[]="Failed to create foreground font manager"; /* ROM0x0073fdc0 */
static const char audio_uart_ring_init_secondary_short[]="[font_manager]Failed to create foreground font manager"; /* ROM0x007202f0 */
static const char audio_uart_ring_init_success[]="Font initialization completed - background: %p, foreground: %p"; /* ROM0x0070c9e4 */
static const char audio_uart_ring_init_success_short[]="[font_manager]Font initialization completed - background: %p, foreground: %p"; /* ROM0x006ee3c8 */
/* Stock 0x46D464 (font_manager_init) */
void audio_uart_display_ring_init(void) {
    audio_uart_display_ring_static_init();
    uint32_t *primary=(uint32_t *)audio_uart_display_ring_construct(
                                 audio_uart_ring_primary_descriptors,4u);
    audio_uart_ring_primary_list_cell=(uint32_t)(uintptr_t)primary;
    if(primary==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,audio_uart_ring_init_module,
                  audio_uart_ring_init_source,audio_uart_ring_init_function,
                  0x261u,audio_uart_ring_init_primary_error);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,
                  audio_uart_ring_init_primary_short,
                  audio_uart_ring_init_primary_short);
        audio_uart_ring_primary_head_cell=0u;
    } else audio_uart_ring_primary_head_cell=(uint32_t)(uintptr_t)
                                              audio_uart_display_ring_head(primary);
    uint32_t *secondary=(uint32_t *)audio_uart_display_ring_construct(
                                 audio_uart_ring_secondary_descriptors,4u);
    audio_uart_ring_secondary_list_cell=(uint32_t)(uintptr_t)secondary;
    if(secondary==0) {
        if(audio_log_flags()&2u)
            audio_log_extended(1u,audio_uart_ring_init_module,
                  audio_uart_ring_init_source,audio_uart_ring_init_function,
                  0x26bu,audio_uart_ring_init_secondary_error);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x04000000u,
                  audio_uart_ring_init_secondary_short,
                  audio_uart_ring_init_secondary_short);
        audio_uart_ring_secondary_head_cell=0u;
    } else audio_uart_ring_secondary_head_cell=(uint32_t)(uintptr_t)
                                                audio_uart_display_ring_head(secondary);
    if(audio_log_flags()&2u)
        audio_log_extended(3u,audio_uart_ring_init_module,
              audio_uart_ring_init_source,audio_uart_ring_init_function,
              0x270u,audio_uart_ring_init_success,
              audio_uart_ring_primary_head_cell,audio_uart_ring_secondary_head_cell);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x0c800000u,
              audio_uart_ring_init_success_short,
              audio_uart_ring_init_success_short,
              audio_uart_ring_primary_head_cell,audio_uart_ring_secondary_head_cell);
}
