/* NemaGFX platform HAL (Ambiq nema_hal.c port for Apollo5; source path not retained).
 * Native 0x513ed0..0x51400a; literal pool 0x51423c..0x51425f (shared with 0x51400a..).
 *
 * This is the platform-integration layer that the NemaGFX library calls through
 * nema_hal.h (IRQ, semaphore, ring-buffer setup). It only uses the public HAL
 * contract; the NemaGFX/NemaVG library internals are not reconstructed here.
 * The GPU interrupt is IRQ 28 (vector slot 0x4380b0 holds 0x513f93). The three
 * CMSIS NVIC helpers are IAR out-of-line copies of core_cm55.h inlines owned by
 * this TU (__NVIC_PRIO_BITS = 4, so priorities are shifted by 4). */
#include <stdint.h>
#include <stddef.h>

#define G2_GPU_IRQN 28
#define G2_GPU_IRQ_PRIORITY 4u        /* AM_IRQ_PRIORITY_DEFAULT */
#define G2_NEMA_REG_INTERRUPT 0xf8u   /* NEMA_INTERRUPT */
#define G2_NEMA_REG_CLID 0x148u       /* NEMA_CLID: last completed command-list id */
#define G2_NEMA_RING_SIZE 0x1300u     /* ring-buffer allocation, pool 0 */
#define G2_SCB_ICSR_PENDSVSET 0x10000000u

/* nema_ringbuffer_t at RAM 0x20073bf0 (24 bytes): bo {size, fd, base_virt,
 * base_phys}, offset +0x10, last_submission_id +0x14. */
extern volatile uint32_t audio_uart_nema_command_state_20073bf0[];
/* last_cl_id, RAM 0x20002e08 (initialised to -1). */
extern volatile uint32_t audio_uart_nema_last_submission;
/* Binary semaphore given from the GPU ISR, RAM 0x20074814. */
extern void *volatile g2_nema_irq_semaphore;
/* Optional completion callback taking last_cl_id, RAM 0x20074818. */
extern void (*volatile g2_nema_irq_callback)(uint32_t cl_id);

extern uint32_t audio_uart_nema_reg_read_51403c(uint32_t offset);             /* nema_reg_read */
extern void audio_uart_nema_reg_write_514046(uint32_t offset, uint32_t value); /* nema_reg_write */
extern void audio_uart_nema_buffer_create_514070(uint32_t *out, uint32_t pool,
                                                 uint32_t size);              /* nema_buffer_create_pool */
extern int32_t audio_uart_nema_ring_initialize_523bf8(void *ring, uint32_t reset); /* nema_rb_init */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src,
                                                 uint32_t len);               /* memcpy */
extern uint32_t audio_os_mutex_dynamic_core_441636(uint32_t length, uint32_t item_size,
                                                   uint32_t type);            /* xQueueGenericCreate */
extern int32_t xQueueGiveFromISR(void *queue, int32_t *woken);

#define G2_NVIC_ISER ((volatile uint32_t *)0xe000e100u)
#define G2_NVIC_ICPR ((volatile uint32_t *)0xe000e280u)
#define G2_NVIC_IPR ((volatile uint8_t *)0xe000e400u)
#define G2_SCB_SHPR ((volatile uint8_t *)0xe000ed18u)
#define G2_SCB_ICSR (*(volatile uint32_t *)0xe000ed04u)

/* __NVIC_EnableIRQ */
void nvic_enable_irq_513ed0(int16_t irqn)
{
    if (irqn >= 0)
        G2_NVIC_ISER[(uint32_t)(int32_t)irqn >> 5] = 1u << ((uint32_t)irqn & 31u);
}

/* __NVIC_ClearPendingIRQ */
void nvic_clear_pending_irq_513eee(int16_t irqn)
{
    if (irqn >= 0)
        G2_NVIC_ICPR[(uint32_t)(int32_t)irqn >> 5] = 1u << ((uint32_t)irqn & 31u);
}

/* __NVIC_SetPriority: system handlers go to SCB->SHPR[(irqn & 0xf) - 4]. */
void nvic_set_priority_513f0c(int16_t irqn, uint32_t priority)
{
    if (irqn >= 0)
        G2_NVIC_IPR[irqn] = (uint8_t)(priority << 4);
    else
        G2_SCB_SHPR[((uint32_t)(int32_t)irqn & 0xfu) - 4u] = (uint8_t)(priority << 4);
}

/* GPU interrupt body: acknowledge until NEMA_CLID is stable, publish it as
 * last_cl_id, wake the waiter and run the optional callback. The ISR flag is
 * not pre-initialised in stock (its stack slot is the pushed r3). */
void nema_gpu_irq_service_513f34(uint32_t unused)
{
    int32_t woken;
    uint32_t previous;
    uint32_t cl_id = audio_uart_nema_reg_read_51403c(G2_NEMA_REG_CLID);

    (void)unused;
    do {
        audio_uart_nema_reg_write_514046(G2_NEMA_REG_INTERRUPT, 0u);
        nvic_clear_pending_irq_513eee(G2_GPU_IRQN);
        previous = cl_id;
        cl_id = audio_uart_nema_reg_read_51403c(G2_NEMA_REG_CLID);
    } while (cl_id != previous);

    audio_uart_nema_last_submission = cl_id;
    xQueueGiveFromISR(g2_nema_irq_semaphore, &woken);
    if (woken != 0)
        G2_SCB_ICSR = G2_SCB_ICSR_PENDSVSET; /* portYIELD_FROM_ISR */
    if (g2_nema_irq_callback != NULL)
        g2_nema_irq_callback(audio_uart_nema_last_submission);
}

/* GPU_IRQHandler (vector table entry for IRQ 28). */
void gpu_irq_handler_513f92(void)
{
    nema_gpu_irq_service_513f34(0u);
}

/* nema_sys_init: clear the GPU interrupt, enable IRQ 28, create the IRQ
 * semaphore once, allocate and map the ring buffer once, then initialise it.
 * Returns the nema_rb_init status (0 on success, which also resets last_cl_id). */
int32_t nema_sys_init_513f9c(void)
{
    volatile uint32_t *ring = audio_uart_nema_command_state_20073bf0;
    int32_t status;

    audio_uart_nema_reg_write_514046(G2_NEMA_REG_INTERRUPT, 0u);
    nvic_set_priority_513f0c(G2_GPU_IRQN, G2_GPU_IRQ_PRIORITY);
    nvic_enable_irq_513ed0(G2_GPU_IRQN);

    if (g2_nema_irq_semaphore == NULL)
        g2_nema_irq_semaphore = (void *)(uintptr_t)
            audio_os_mutex_dynamic_core_441636(1u, 0u, 3u); /* xSemaphoreCreateBinary */

    if (ring[3] == 0u) { /* bo.base_phys */
        uint32_t bo[4];
        audio_uart_nema_buffer_create_514070(bo, 0u, G2_NEMA_RING_SIZE);
        audio_uart_display_area_copy_439c04((void *)(uintptr_t)ring, bo, sizeof bo);
        (void)ring[2]; /* nema_buffer_map: base_virt, result unused */
    }

    status = audio_uart_nema_ring_initialize_523bf8((void *)(uintptr_t)ring, 1u);
    if (status == 0)
        audio_uart_nema_last_submission = UINT32_MAX;
    return status;
}
