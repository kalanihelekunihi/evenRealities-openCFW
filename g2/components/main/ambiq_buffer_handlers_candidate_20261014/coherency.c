/* Apollo S200 Ambiq buffer update, flush, and invalidate adapters. */
#include <stdint.h>

extern void audio_uart_lv_memzero_48949c(void *,uint32_t);
extern uint32_t audio_uart_nema_pool_contains_514148(uint32_t,uint32_t);
extern void audio_uart_nema_cl_buffer_destroy_5140c6(void *);
extern void audio_uart_nema_buffer_flush_5140ea(void *);
extern void audio_uart_nema_buffer_invalidate_51411a(void *);
extern void audio_uart_lvgl_log(uint32_t,const char *,uint32_t,
                                const char *,const char *,...);

static const char buffer_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\lvgl_v9.3\\LVGL\\src\\draw\\ambiq\\lv_draw_ambiq_buffer.c";
static const char asserted[] = "Asserted at expression: %s (%s)";
static const char outside_pool[] = "Buffer is not within the pool";
static const char free_expression[] =
    "nema_buffer_is_within_pool(pool, (uint32_t)buf, 0)";
static const char data_expression[] =
    "nema_buffer_is_within_pool(pool, (uint32_t)draw_buf->data, draw_buf->data_size)";
static const char free_function[] = "lv_draw_ambiq_buffer_free_core";
static const char flush_function[] = "lv_draw_ambiq_buffer_flush_core";
static const char invalidate_function[] =
    "lv_draw_ambiq_buffer_invalidate_core";

static void buffer_outside_pool(uint32_t line,const char *function,
                                 const char *expression) {
    audio_uart_lvgl_log(3u,buffer_path,line,function,
                        asserted,expression,outside_pool);
    for (;;) *(volatile uint32_t *)(uintptr_t)UINT32_MAX = 0u;
}

void audio_uart_ambiq_buffer_update_53cf8a(uint32_t pool,uint32_t data) {
    uint32_t descriptor[4];
    audio_uart_lv_memzero_48949c(descriptor,16u);
    descriptor[1] = pool;
    descriptor[2] = data;
    descriptor[3] = data;
    if (audio_uart_nema_pool_contains_514148(pool,data) == 0u)
        buffer_outside_pool(0x44u,free_function,free_expression);
    audio_uart_nema_cl_buffer_destroy_5140c6(descriptor);
}

void audio_uart_ambiq_buffer_mask_53d006(uint32_t pool,
                                            const uint32_t *draw_buffer,
                                            uint32_t ignored) {
    (void)ignored;
    if ((draw_buffer[0] & 0x00100000u) == 0u) return;
    uint32_t descriptor[4] = {draw_buffer[3],pool,
                               draw_buffer[4],draw_buffer[4]};
    if (audio_uart_nema_pool_contains_514148(
            pool,draw_buffer[4]) == 0u)
        buffer_outside_pool(0x6bu,flush_function,data_expression);
    audio_uart_nema_buffer_flush_5140ea(descriptor);
}

void audio_uart_ambiq_buffer_layout_53d062(uint32_t pool,
                                              const uint32_t *draw_buffer,
                                              uint32_t ignored) {
    (void)ignored;
    uint32_t descriptor[4] = {draw_buffer[3],pool,
                               draw_buffer[4],draw_buffer[4]};
    if (audio_uart_nema_pool_contains_514148(
            pool,draw_buffer[4]) == 0u)
        buffer_outside_pool(0x78u,invalidate_function,data_expression);
    audio_uart_nema_buffer_invalidate_51411a(descriptor);
}
