/* UART sync DMA write native 0x584c98 and DMA control helpers 0x584a64/
 * 0x584a38 plus status 0x58e754. Product TX RAM, mutex, and semaphore
 * remain typed cells; this executes genuine MMIO and cache-maintenance flow. */
#include <stdint.h>
extern void *g2_uart_sync_driver; /* RAM0x20074610 */
extern volatile uint8_t g2_uart_sync_started; /* RAM0x20074fc9 */
extern void *g2_uart_sync_semaphore_handle; /* RAM0x2007461c */
extern void *g2_uart_sync_mutex; /* RAM0x20074620 */
extern volatile uint8_t g2_uart_sync_write_error; /* RAM0x20074fca */
extern uint8_t g2_uart_sync_tx_buffer[0x400]; /* RAM0x20379da0 */
extern int32_t audio_file_mutex_acquire(void *,uint32_t); /* selected 0x4497b6 */
extern int32_t audio_file_mutex_release(void *); /* selected 0x44981c */
extern int32_t audio_semaphore_acquire(void *,uint32_t); /* selected 0x44994e */
extern uint32_t g2_flashdb_candidate_tick(void); /* selected 0x4490cc */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */
extern void audio_delay_us_selected(uint32_t); /* selected 0x4807a0 */
static volatile uint32_t *uart_reg(uint32_t offset) {
    return (volatile uint32_t *)(uintptr_t)(0x40039000u+offset);
}
/* Stock 0x584A64 (uart_sync_dma_stop_584a64) */
void uart_sync_dma_stop_584a64(void) {
    *uart_reg(0x48u)=0u;
    *uart_reg(4u)&=~0x30u;
    *uart_reg(0x44u)=0x1800u;
}
/* Stock 0x584A38 (uart_sync_dma_start_584a38) */
void uart_sync_dma_start_584a38(uint32_t source,uint32_t count) {
    *uart_reg(0x48u)=0u;
    *uart_reg(0x4cu)=source;
    *uart_reg(0x50u)=count;
    *uart_reg(0x38u)|=0x1800u;
    *uart_reg(0x44u)=0x1821u;
    *uart_reg(4u)&=~0x30u;
    __asm__ volatile("dmb sy" ::: "memory");
    *uart_reg(0x48u)=10u;
}
/* Stock 0x58E754 (am_hal_uart_flags_get) */
static uint32_t driver_status(void *handle,uint32_t *status) {
    if(handle==0 || (*(uint32_t *)handle&0x1ffffffu)!=0x1ea9e06u)
        return 2u;
    if(status==0) return 6u;
    uint32_t instance=*(uint32_t *)((uint8_t *)handle+0x28u);
    *status=*(volatile uint32_t *)(uintptr_t)
        (0x40039000u+instance*0x1000u+0x18u);
    return 0u;
}
uint32_t audio_uart_sync_write(const void *bytes,uint32_t size) {
    if(bytes==0 || size==0u || size>0x400u ||
       g2_uart_sync_started!=1u || g2_uart_sync_driver==0 ||
       g2_uart_sync_mutex==0 || g2_uart_sync_semaphore_handle==0)
        return 1u;
    if(audio_file_mutex_acquire(g2_uart_sync_mutex,UINT32_MAX)!=0) return 1u;
    (void)g2_flashdb_candidate_tick();
    (void)audio_queue_copy_bytes(g2_uart_sync_tx_buffer,bytes,size);
    uintptr_t source=(uintptr_t)g2_uart_sync_tx_buffer;
    uint32_t aligned=(size+31u)&~31u;
    if(aligned!=0u) {
        uint32_t remaining=(uint32_t)(source&31u)+aligned;
        __asm__ volatile("dsb sy" ::: "memory");
        uintptr_t address=source;
        do {
            *(volatile uint32_t *)(uintptr_t)0xe000ef68u=(uint32_t)address;
            address+=32u;
            remaining-=32u;
        } while((int32_t)remaining>0);
        __asm__ volatile("dsb sy\n\tisb sy" ::: "memory");
    }
    (void)audio_semaphore_acquire(g2_uart_sync_semaphore_handle,0u);
    g2_uart_sync_write_error=0u;
    uart_sync_dma_stop_584a64();
    uart_sync_dma_start_584a38((uint32_t)source,size);
    if(audio_semaphore_acquire(g2_uart_sync_semaphore_handle,100u)!=0) {
        uart_sync_dma_stop_584a64();
        g2_uart_sync_write_error=0u;
        (void)audio_file_mutex_release(g2_uart_sync_mutex);
        return 1u;
    }
    if(g2_uart_sync_write_error!=0u) {
        g2_uart_sync_write_error=0u;
        (void)audio_file_mutex_release(g2_uart_sync_mutex);
        return 1u;
    }
    uint32_t status=0u;
    for(uint32_t attempts=0u;attempts<100u;++attempts) {
        (void)driver_status(g2_uart_sync_driver,&status);
        if((status&8u)==0u) break;
        audio_delay_us_selected(10u);
    }
    (void)audio_file_mutex_release(g2_uart_sync_mutex);
    return 0u;
}
