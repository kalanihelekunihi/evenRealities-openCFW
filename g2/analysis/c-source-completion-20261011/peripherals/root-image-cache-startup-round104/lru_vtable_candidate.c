/* Source-defined backend dispatch corresponding to authenticated ROM0x73f478. */
#include <stdint.h>
extern void *audio_uart_font_lru_allocate(void); /* 0x5c2bee */
extern uint32_t audio_uart_font_lru_initialize(void *); /* 0x5c2c54 */
extern void audio_uart_font_lru_destroy(void *); /* 0x5c2e0c */
extern void *audio_uart_font_lru_lookup(void *,const void *); /* 0x5c2e4c */
extern void *audio_uart_font_lru_add(void *,const void *); /* 0x5c2f32 */
extern void audio_uart_font_lru_remove(void *,void *,uint32_t); /* 0x5c2fd4 */
extern void audio_uart_font_lru_evict(void *,const void *,uint32_t); /* 0x5c3098 */
extern void audio_uart_font_lru_clear(void *,uint32_t); /* 0x5c315a */
extern void *audio_uart_font_lru_get_victim(void *,uint32_t); /* 0x5c3222 */
extern uint8_t audio_uart_font_lru_reserve(void *,const void *,uint32_t); /* 0x5c328a */
const uintptr_t audio_uart_font_cache_backend_vtable[10]={
    (uintptr_t)&audio_uart_font_lru_allocate,
    (uintptr_t)&audio_uart_font_lru_initialize,
    (uintptr_t)&audio_uart_font_lru_destroy,
    (uintptr_t)&audio_uart_font_lru_lookup,
    (uintptr_t)&audio_uart_font_lru_add,
    (uintptr_t)&audio_uart_font_lru_remove,
    (uintptr_t)&audio_uart_font_lru_evict,
    (uintptr_t)&audio_uart_font_lru_clear,
    (uintptr_t)&audio_uart_font_lru_get_victim,
    (uintptr_t)&audio_uart_font_lru_reserve,
};

extern uint32_t audio_uart_lv_cache_size_lru_init_5c2d30(void *);
const uintptr_t audio_uart_lv_cache_size_backend_vtable[10]={
    (uintptr_t)&audio_uart_font_lru_allocate,
    (uintptr_t)&audio_uart_lv_cache_size_lru_init_5c2d30,
    (uintptr_t)&audio_uart_font_lru_destroy,
    (uintptr_t)&audio_uart_font_lru_lookup,
    (uintptr_t)&audio_uart_font_lru_add,
    (uintptr_t)&audio_uart_font_lru_remove,
    (uintptr_t)&audio_uart_font_lru_evict,
    (uintptr_t)&audio_uart_font_lru_clear,
    (uintptr_t)&audio_uart_font_lru_get_victim,
    (uintptr_t)&audio_uart_font_lru_reserve,
};
