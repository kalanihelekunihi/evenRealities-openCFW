/* Native LVGL cache acquire-or-create 0x4d4f90, add 0x4d51c0, evict 0x4d5172. */
#include <stdint.h>
extern uint32_t audio_uart_lv_lock_core(void *);
extern uint32_t audio_uart_lv_unlock_core(void *);
extern void audio_uart_font_cache_retain(void *);
extern void *audio_uart_font_cache_acquire_data(void *);
extern void *audio_uart_font_cache_info(void *);
extern void audio_uart_font_cache_entry_delete(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,const char *,const char *,...);
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\misc\\cache\\lv_cache.c";
typedef void *(*lookup_fn)(void *,const void *,uint32_t);
typedef void (*remove_fn)(void *,void *,uint32_t);
typedef void *(*create_fn)(void *,const void *,uint32_t);
typedef uint32_t (*space_fn)(void *,const void *,uint32_t,uint32_t);
typedef void *(*victim_fn)(void *,uint32_t);
typedef uint32_t (*initialize_fn)(void *,uint32_t);
typedef void (*destroy_fn)(void *,uint32_t);
/* Full native4d4f90..4d5094; preserve fast existing-entry acquire and fresh class/ops loads. */
