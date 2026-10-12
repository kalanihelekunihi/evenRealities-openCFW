#include <stdint.h>
extern void *g2_tlsf_control_create_4d06b4(void *);
extern void *g2_tlsf_add_pool_4d0608(void *,void *,uint32_t);
extern void *audio_uart_mutex_dynamic_create(uint32_t);
extern void g2_file_heap_error_log(const char *);
extern void audio_uart_heap_memory_configure_4840c8(void);
void *g2_tlsf_create_with_pool_4d06ec(void *memory,uint32_t bytes) {
    void *control=g2_tlsf_control_create_4d06b4(memory);
    (void)g2_tlsf_add_pool_4d0608(control,(void *)((uintptr_t)memory+0xc74u),bytes-0xc74u);
    return control;
}
void audio_uart_lv_pool_initialize_48413c(void *cell,void *memory,uint32_t bytes) {
    volatile uint32_t *pool=cell;
    pool[1]=(uint32_t)(uintptr_t)g2_tlsf_create_with_pool_4d06ec(memory,bytes);
    if(pool[1]==0u) {
        g2_file_heap_error_log((const char *)(uintptr_t)0x75165cu);
        for(;;)__asm__ volatile("" ::: "memory");
    }
    pool[0]=(uint32_t)(uintptr_t)audio_uart_mutex_dynamic_create(1u);
    if(pool[0]==0u) {
        g2_file_heap_error_log((const char *)(uintptr_t)0x75d650u);
        for(;;)__asm__ volatile("" ::: "memory");
    }
    pool[2]=0u;pool[3]=0u;pool[4]=bytes;pool[5]=(uint32_t)(uintptr_t)memory;
}
void audio_uart_heap_initialize_4842e6(void) {
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000338u,(void *)(uintptr_t)0x20279670u,0x2d000u);
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000354u,(void *)(uintptr_t)0x2013be70u,0xcd000u);
    audio_uart_lv_pool_initialize_48413c((void *)(uintptr_t)0x20000370u,(void *)(uintptr_t)0x20378d9cu,0x400u);
    audio_uart_heap_memory_configure_4840c8();
    *(volatile uint8_t *)(uintptr_t)0x2000036cu=0u;
    *(volatile uint8_t *)(uintptr_t)0x20000388u=0u;
}
