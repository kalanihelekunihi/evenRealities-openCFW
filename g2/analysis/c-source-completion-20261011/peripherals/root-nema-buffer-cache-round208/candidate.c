#include <stdint.h>
extern void *audio_uart_nema_pool_select_514050(uint32_t);
extern uint32_t audio_uart_cache_clean_range_47510e(const uint32_t *);
extern void audio_ble_privacy_cache_maintenance(const uint32_t *,uint8_t);
/* Native5140ea..51411a: conditional clean, unconditional DSB. */
void audio_uart_nema_buffer_flush_5140ea(void *buffer) {
    volatile uint32_t *b=buffer;
    const volatile uint8_t *pool=audio_uart_nema_pool_select_514050(b[1]);
    if(pool[24]!=0u) {
        uint32_t size=b[0];
        uint32_t physical=b[3];
        uint32_t range[2]={physical,size};
        (void)audio_uart_cache_clean_range_47510e(range);
    }
    __asm__ volatile("dsb sy" ::: "memory");
}
/* Native51411a..514148: conditional invalidate, no extra barrier here. */
void audio_uart_nema_buffer_invalidate_51411a(void *buffer) {
    volatile uint32_t *b=buffer;
    const volatile uint8_t *pool=audio_uart_nema_pool_select_514050(b[1]);
    if(pool[24]!=0u) {
        uint32_t size=b[0];
        uint32_t physical=b[3];
        uint32_t range[2]={physical,size};
        audio_ble_privacy_cache_maintenance(range,0u);
    }
}
/* Native514148..51416c: two fresh base loads; unsigned wrapped interval test. */
uint32_t audio_uart_nema_pool_contains_514148(uint32_t id,uint32_t address,uint32_t size) {
    const volatile uint32_t *pool=audio_uart_nema_pool_select_514050(id);
    uint32_t base_first=pool[5];
    uint32_t base_second=pool[5];
    uint32_t length=pool[4];
    uint32_t end=base_second+length;
    if(address<base_first) return 0u;
    return end>=address+size;
}
