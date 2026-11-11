/* Native LVGL list/tick/lock/wait leaves for 0x464344. */
#include <stdint.h>
extern uint8_t audio_uart_lv_tick_state[]; /* RAM0x2006f600 */
extern uint8_t audio_uart_lv_lock_cell[]; /* RAM0x2006f718 */
extern uint8_t audio_uart_display_lv_state[]; /* RAM0x2006f548 */
extern int32_t xQueueTakeMutexRecursive(void *,uint32_t);
extern int32_t xQueueGiveMutexRecursive(void *);
extern void *audio_uart_mutex_dynamic_create(uint32_t); /* 0x4416d6 */
extern void stock_enter_critical(void); /* 0x4420d0 */
extern void stock_exit_critical(void); /* 0x4420e8 */
extern void lv_log_add(uint32_t,const char *,uint32_t,
                                 const char *,const char *,...); /* 0x44d25c */
void audio_uart_lv_list_remove(void *,void *); /* 0x482c0e */
extern uint8_t audio_uart_lv_heap_pool[] __asm__("g2_stock_ram_20000338"); /* RAM0x20000338, DAT_0048436c */
extern int32_t xQueueSemaphoreTake(void *,uint32_t); /* selected native 0x441c44 */
extern int32_t audio_uart_queue_send(void *,const void *,uint32_t,uint32_t); /* selected 0x4417ee */
extern uint32_t g2_tlsf_block_size(void *); /* selected 0x4cfd70 */
extern void g2_file_pool_free(void *,void *); /* selected 0x4d0808 */
extern void audio_uart_lv_assert_null(void); /* native 0x464512 logging/fault */
void audio_uart_lv_timer_delete(void *);
void audio_uart_lv_timer_pause(void *);
uint32_t lv_mutex_lock(void *);
uint32_t lv_mutex_unlock(void *);

/* 0x4d477a/0x4d47cc/0x4d4666/0x4d4696 are upstream lv_freertos.c
 * prvMutexInit/prvCheckMutexInit/lv_mutex_lock/lv_mutex_unlock; the hand
 * copies were removed and callers use lv_mutex_lock/lv_mutex_unlock. */

/* Retired: stock 0x473482 is upstream lv_tick_get (lvgl/src/tick/lv_tick.c); this name is a link alias. */
uint32_t audio_uart_lv_tick(void);
/* Retired: stock 0x4734a0 is upstream lv_tick_elaps (lvgl/src/tick/lv_tick.c); this name is a link alias. */
uint32_t audio_uart_lv_elapsed(uint32_t start);
/* 0x46467c lv_timer_time_remaining (static) and 0x49acba/0x49acc4
 * lv_lock/lv_unlock are upstream (lv_timer.c, lv_os.c); the unreferenced
 * hand copies were removed. */
/* Retired: stock 0x482c0e is upstream lv_ll_remove (lvgl/src/misc/lv_ll.c); this name is a link alias. */
void audio_uart_lv_list_remove(void *list,void *node);
/* 0x464604 lv_timer_exec (static) and 0x4644ee lv_timer_delete are upstream
 * lv_timer.c; the unreferenced hand copies were removed. */
/* Retired: stock 0x46450c is upstream lv_timer_pause (lvgl/src/misc/lv_timer.c); this name is a link alias. */
void audio_uart_lv_timer_pause(void *timer);
/* Retired 2026-10-30: audio_uart_lv_free was a second copy of stock 0x44f758, which is
 * upstream lv_free (lvgl/src/stdlib/lv_mem.c): its static slot is lv_global+0x64, the
 * upstream zero_mem, and audio_uart_lv_heap_free is a compose alias of lv_free. Callers
 * use lv_free. */
