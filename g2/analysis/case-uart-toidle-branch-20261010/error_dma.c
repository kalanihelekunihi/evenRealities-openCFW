#include <stdint.h>
extern uint32_t case_dma_abort_it(void *);
static void clear_atomic(volatile uint32_t *,uint32_t);
void case_dma_abort_on_error(uint8_t *);

/* Selected public-entry error matrix: DMAR set, nonnull DMA, at least one
 * enabled error flag. Other IRQ families remain outside this source. */
void case_uart_error_dma_matrix(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    uint32_t errors=isr&0x80fu;
    if (!errors || !((cr3&0x10000001u)||(cr1&0x4000120u)))return;
    uint32_t *error=(uint32_t *)(void *)(handle+0x90);
    if ((isr&1u)&&(cr1&0x100u)){uart[8]=1u;*error|=1u;}
    if ((isr&2u)&&(cr3&1u)){uart[8]=2u;*error|=4u;}
    if ((isr&4u)&&(cr3&1u)){uart[8]=4u;*error|=2u;}
    if ((isr&8u)&&((cr1&0x20u)||(cr3&0x10000001u))){uart[8]=8u;*error|=8u;}
    if ((isr&0x800u)&&(cr1&0x4000000u)){uart[8]=0x800u;*error|=0x20u;}
    if (!*error)return;
    if ((isr&0x20u)&&((cr1&0x20u)||(cr3&0x10000000u))) {
        void (*rx)(uint8_t *)=*(void (**)(uint8_t *))(void *)(handle+0x74);
        if (rx)rx(handle);
    }
    uint32_t live_cr3=uart[2],live_error=*error;
    if (!(live_cr3&0x40u) && !(live_error&0x28u)) {
        /* Fixed-image weak ErrorCallback is a no-op. */
        *error=0u;
        return;
    }
    clear_atomic(&uart[0],0x120u);
    clear_atomic(&uart[2],0x10000001u);
    if (*(uint32_t *)(void *)(handle+0x6c)==1u)
        clear_atomic(&uart[0],0x10u);
    *(uint32_t *)(void *)(handle+0x8c)=0x20u;
    *(uint32_t *)(void *)(handle+0x6c)=0u;
    *(uint32_t *)(void *)(handle+0x74)=0u;
    if (!(uart[2]&0x40u))return;
    clear_atomic(&uart[2],0x40u);
    uint8_t *dma=*(uint8_t **)(void *)(handle+0x80);
    if (!dma)return; /* stock 0x0800603a..0x08006078: weak no-op error callback */
    *(void (**)(uint8_t *))(void *)(dma+0x38)=case_dma_abort_on_error;
    if (case_dma_abort_it(dma)!=0u)
        (*(void (**)(uint8_t *))(void *)(dma+0x38))(dma);
}

static void clear_atomic(volatile uint32_t *reg,uint32_t mask)
{
    uint32_t saved,one=1;
    __asm volatile("mrs %0, primask\nmsr primask, %1"
                   : "=&r"(saved):"r"(one):"memory");
    *reg &= ~mask;
    __asm volatile("msr primask, %0"::"r"(saved):"memory");
}

void case_dma_abort_on_error(uint8_t *dma)
{
    uint8_t *handle=*(uint8_t **)(void *)(dma+0x28);
    *(uint16_t *)(void *)(handle+0x5e)=0;
    *(uint16_t *)(void *)(handle+0x56)=0;
    /* Stock weak HAL_UART_ErrorCallback at 0x08005f42 is a no-op. */
}

/* Selected public-entry domain: ORE enabled, DMAR set, nonnull DMA handle,
 * no RX-ready flag. Other error combinations remain outside this source. */
void case_uart_error_dma_branch(uint8_t *handle)
{
    volatile uint32_t *uart=*(volatile uint32_t **)(void *)handle;
    uint32_t isr=uart[7],cr1=uart[0],cr3=uart[2];
    if (!(isr&8u) || !(cr1&0x20u) || !(cr3&0x40u))return;
    uart[8]=8u;
    *(uint32_t *)(void *)(handle+0x90)|=8u;
    /* UART_EndRxTransfer */
    clear_atomic(&uart[0],0x120u);
    clear_atomic(&uart[2],0x10000001u);
    if (*(uint32_t *)(void *)(handle+0x6c)==1u)
        clear_atomic(&uart[0],0x10u);
    *(uint32_t *)(void *)(handle+0x8c)=0x20u;
    *(uint32_t *)(void *)(handle+0x6c)=0u;
    *(uint32_t *)(void *)(handle+0x74)=0u;
    clear_atomic(&uart[2],0x40u);
    uint8_t *dma=*(uint8_t **)(void *)(handle+0x80);
    *(void (**)(uint8_t *))(void *)(dma+0x38)=case_dma_abort_on_error;
    if (case_dma_abort_it(dma)!=0u)
        (*(void (**)(uint8_t *))(void *)(dma+0x38))(dma);
}
