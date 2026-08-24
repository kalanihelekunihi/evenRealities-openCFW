#include "drv_gx8002b_host.h"
#include <stddef.h>
#include <string.h>

uint32_t host_gx_iser[16];
uint32_t host_gx_icer[16];
uint8_t host_gx_ipr[512];
uint8_t host_gx_shpr_storage[32];
uint8_t host_gx_power_state;
uint8_t host_gx_i2s_state;
void *host_gx_i2s_handle;
uint8_t host_gx_config;
uint8_t host_gx_transfer;
int16_t host_gx_irq;
uint32_t host_gx_calls[64];
uint32_t host_gx_call_count;
uint32_t host_gx_gpio_index[8];
uint32_t host_gx_gpio_value[8];
uint32_t host_gx_gpio_count;
uint32_t host_gx_delays[8];
uint32_t host_gx_delay_count;
uint32_t host_gx_interrupt_status_value;
uint32_t host_gx_dma_buffer_value;
uintptr_t host_gx_cache_address;
uint32_t host_gx_cache_length;
uint32_t host_gx_cache_clean;
int32_t host_gx_last_irq;
uint32_t host_gx_last_priority;
uint32_t host_gx_rx_notify_count;
uint32_t host_gx_audio_notify_count;
uint32_t host_gx_power_on_count;
uint32_t host_gx_power_off_count;

enum {
    C_DSB=1, C_ISB, C_BOARD_INIT, C_INITIALIZE, C_POWER_ACTIVE,
    C_CONFIGURE, C_ENABLE, C_DMA_CONFIGURE, C_NVIC_PRIORITY,
    C_NVIC_ENABLE, C_GLOBAL_ENABLE, C_DMA_START, C_NVIC_DISABLE,
    C_BOARD_DEINIT, C_POWER_OFF, C_DISABLE, C_DEINITIALIZE,
    C_INT_STATUS, C_INT_CLEAR, C_INT_SERVICE, C_CACHE
};

static void call(uint32_t id) { host_gx_calls[host_gx_call_count++] = id; }

void host_gx_reset(void)
{
    memset(host_gx_iser, 0, sizeof(host_gx_iser));
    memset(host_gx_icer, 0, sizeof(host_gx_icer));
    memset(host_gx_ipr, 0, sizeof(host_gx_ipr));
    memset(host_gx_shpr_storage, 0, sizeof(host_gx_shpr_storage));
    memset(host_gx_calls, 0, sizeof(host_gx_calls));
    memset(host_gx_gpio_index, 0, sizeof(host_gx_gpio_index));
    memset(host_gx_gpio_value, 0, sizeof(host_gx_gpio_value));
    memset(host_gx_delays, 0, sizeof(host_gx_delays));
    host_gx_power_state=host_gx_i2s_state=0;
    host_gx_i2s_handle=(void *)(uintptr_t)0x11110000u;
    host_gx_irq=44;
    host_gx_call_count=host_gx_gpio_count=host_gx_delay_count=0;
    host_gx_interrupt_status_value=0;
    host_gx_dma_buffer_value=0x20001234u;
    host_gx_cache_address=0;
    host_gx_cache_length=host_gx_cache_clean=0;
    host_gx_last_irq=0;
    host_gx_last_priority=0;
    host_gx_rx_notify_count=host_gx_audio_notify_count=0;
    host_gx_power_on_count=host_gx_power_off_count=0;
}

void host_gx_dsb(void){call(C_DSB);} void host_gx_isb(void){call(C_ISB);}
void host_gx_gpio_write(uint32_t i,uint32_t v){host_gx_gpio_index[host_gx_gpio_count]=i;host_gx_gpio_value[host_gx_gpio_count++]=v;}
uint32_t host_gx_delay(uint32_t ms){host_gx_delays[host_gx_delay_count++]=ms;return 0;}
void host_gx_board_i2s_init(uint32_t i,uint8_t a){(void)i;(void)a;call(C_BOARD_INIT);}
void host_gx_board_i2s_deinit(uint32_t i,uint8_t a){(void)i;(void)a;call(C_BOARD_DEINIT);}
void host_gx_irq_enable_global(void){call(C_GLOBAL_ENABLE);}
uint32_t host_gx_i2s_initialize(uint32_t m,void **h){(void)m;call(C_INITIALIZE);*h=(void *)(uintptr_t)0x22220000u;return 0;}
uint32_t host_gx_i2s_deinitialize(void *h){(void)h;call(C_DEINITIALIZE);return 0;}
uint32_t host_gx_i2s_power_control(void *h,uint32_t s,bool r){(void)h;(void)r;call(s==0?C_POWER_ACTIVE:C_POWER_OFF);return 0;}
uint32_t host_gx_i2s_configure(void *h,void *c){(void)h;(void)c;call(C_CONFIGURE);return 0;}
uint32_t host_gx_i2s_enable(void *h){(void)h;call(C_ENABLE);return 0;}
uint32_t host_gx_i2s_disable(void *h){(void)h;call(C_DISABLE);return 0;}
uint32_t host_gx_i2s_dma_configure(void *h,void *c,void *t){(void)h;(void)c;(void)t;call(C_DMA_CONFIGURE);return 0;}
uint32_t host_gx_i2s_dma_start(void *h,void *c){(void)h;(void)c;call(C_DMA_START);return 0;}
uint32_t host_gx_i2s_dma_get_buffer(void *h,uint32_t d){(void)h;(void)d;return host_gx_dma_buffer_value;}
uint32_t host_gx_i2s_interrupt_status(void *h,uint32_t *s,bool e){(void)h;(void)e;call(C_INT_STATUS);*s=host_gx_interrupt_status_value;return 0;}
uint32_t host_gx_i2s_interrupt_clear(void *h,uint32_t s){(void)h;(void)s;call(C_INT_CLEAR);return 0;}
uint32_t host_gx_i2s_interrupt_service(void *h,uint32_t s,void *c){(void)h;(void)s;(void)c;call(C_INT_SERVICE);return 0;}
uint32_t host_gx_cache_invalidate(void *d,uint32_t clean){uintptr_t *p=d;call(C_CACHE);host_gx_cache_address=p[0];host_gx_cache_length=*(uint32_t *)(p+1);host_gx_cache_clean=clean;return 0;}
void host_gx_rx_notify(void){++host_gx_rx_notify_count;}
void host_gx_audio_notify(void){++host_gx_audio_notify_count;}
void host_gx_nvic_enable(int32_t i){call(C_NVIC_ENABLE);host_gx_last_irq=i;}
void host_gx_nvic_disable(int32_t i){call(C_NVIC_DISABLE);host_gx_last_irq=i;}
void host_gx_nvic_set_priority(int32_t i,uint32_t p){call(C_NVIC_PRIORITY);host_gx_last_irq=i;host_gx_last_priority=p;}
void host_gx_power_on(void){++host_gx_power_on_count;}
void host_gx_power_off(void){++host_gx_power_off_count;}
