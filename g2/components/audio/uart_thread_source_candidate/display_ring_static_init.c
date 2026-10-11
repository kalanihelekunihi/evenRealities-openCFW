/* Native ring configuration loading 0x46d29a. Product cells remain imported. */
#include <stdint.h>
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* 0x43c0e4 */
extern void audio_uart_ring_config_lock(void); /* 0x46f65e */
extern void audio_uart_ring_config_unlock(void); /* 0x46f674 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* 0x439be4 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uint8_t audio_uart_ring_config_workspace[]; /* RAM0x20324600, 0x5000 bytes */
extern uint32_t audio_uart_ring_config_primary[]; /* address0x80100000, product record */
extern uint32_t audio_uart_ring_config_secondary[]; /* address0x80700000, product record */
extern uint32_t audio_uart_ring_active[]; /* RAM0x20002c00, >=7 words */
extern uint32_t audio_uart_ring_secondary_active[]; /* RAM0x20002c24, >=7 words */
extern uint8_t audio_uart_ring_config_name[16]; /* RAM0x20073e94 */
extern uint8_t audio_uart_ring_config_idle; /* RAM0x20074fe3, byte access native */
extern uint32_t audio_uart_font_glyph_cache_callback(void *,void *,uint32_t,uint32_t); /* Thumb callback0x46d239 */
static const char audio_uart_ring_config_module[]="font_manager"; /* ROM0x00787a50 */
static const char audio_uart_ring_config_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\common\\lvgl_font_manager.c"; /* ROM0x006fb45c */
static const char audio_uart_ring_config_fn[]="_xip_font_configure"; /* ROM0x00781214 */
static const char audio_uart_ring_config_hit[]="XIP font load from flash, Name = %s"; /* ROM0x007568a0 */
static const char audio_uart_ring_config_miss[]="XIP font load error!"; /* ROM0x007795d4 */
static const char audio_uart_ring_config_hit_short[]="[font_manager]XIP font load from flash, Name = %s"; /* ROM0x0072aa78 */
static const char audio_uart_ring_config_miss_short[]="[font_manager]XIP font load error!"; /* ROM0x007568c4 */
static void ring_config_log(uint32_t found,uint32_t line,const uint32_t *record) {
    if(audio_log_flags()&2u) {
        if(found)
            audio_log_extended(2u,audio_uart_ring_config_module,
                 audio_uart_ring_config_source,audio_uart_ring_config_fn,
                 line,audio_uart_ring_config_hit,record+1u);
        else
            audio_log_extended(2u,audio_uart_ring_config_module,
                 audio_uart_ring_config_source,audio_uart_ring_config_fn,
                 line,audio_uart_ring_config_miss);
    }
    if((audio_log_flags()&1u)||(audio_log_flags()&4u)) {
        if(found) (void)compressed_log_output(0x08400000u,
                    audio_uart_ring_config_hit_short,
                    audio_uart_ring_config_hit_short,record+1u);
        else (void)compressed_log_output(0x08000000u,
                    audio_uart_ring_config_miss_short,
                    audio_uart_ring_config_miss_short);
    }
}
void audio_uart_display_ring_static_init(void) {
    audio_uart_buffer_zero(audio_uart_ring_config_workspace,0x5000u,0u);
    audio_uart_ring_config_lock();
    const uint32_t *first=audio_uart_ring_config_primary;
    uint32_t *active=audio_uart_ring_active;
    if(first[0]==0x5a5a5a5au) {
        ring_config_log(1u,0x1feu,first);
        active[6]=first[13];
        uint16_t value=*(const uint16_t *)(const void *)(first+14u);
        if(value!=UINT16_MAX) active[3]=value;
        value=*(const uint16_t *)(const void *)((const uint8_t *)first+0x3au);
        if(value!=UINT16_MAX) active[4]=value;
        (void)audio_queue_copy_bytes(audio_uart_ring_config_name,first+9u,16u);
        audio_uart_ring_config_idle=
             *(const uint32_t *)(const void *)(uintptr_t)(active[6]+0xcu)==0u;
        active[0]=(uint32_t)(uintptr_t)audio_uart_font_glyph_cache_callback;
    } else {
        ring_config_log(0u,0x210u,first);
        active[6]=0u;
    }
    const uint32_t *second=audio_uart_ring_config_secondary;
    uint32_t *secondary=audio_uart_ring_secondary_active;
    if(second[0]==0x5a5a5a5au) {
        ring_config_log(1u,0x216u,second);
        secondary[6]=second[13];
        uint16_t value=*(const uint16_t *)(const void *)(second+14u);
        if(value!=UINT16_MAX) secondary[3]=value;
        value=*(const uint16_t *)(const void *)((const uint8_t *)second+0x3au);
        if(value!=UINT16_MAX) secondary[4]=value;
    } else {
        ring_config_log(0u,0x21fu,second);
        secondary[6]=0u;
    }
    audio_uart_ring_config_unlock();
}
