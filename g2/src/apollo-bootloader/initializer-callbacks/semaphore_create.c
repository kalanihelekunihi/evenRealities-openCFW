/* Locked bootloader semaphore416762, counting constructors419e62/419e94,
 * and queue destroy41a470. Reconstructed ARM32 ABI; no speculative cleanup. */
#include <stdint.h>
extern uint32_t opencfw_bl_context_guard(void);
extern uintptr_t opencfw_bl_kernel_queue_create_dynamic(uint32_t,uint32_t,uint32_t);
extern uintptr_t opencfw_bl_kernel_queue_create_static(uint32_t,uint32_t,uintptr_t,uintptr_t,uint32_t);
extern uint32_t opencfw_bl_kernel_queue_put_blocking(uintptr_t,uintptr_t,uint32_t,uint32_t);
extern void opencfw_bl_rtos_free(uintptr_t);
extern uint32_t opencfw_bl_mask_interrupts(void);
static _Noreturn void fatal(void) {
    (void)opencfw_bl_mask_interrupts();
    *(volatile uint32_t *)(uintptr_t)UINT32_MAX=0;
    for (;;) __asm__ volatile("b ." ::: "memory");
}
void opencfw_boot_semaphore_queue_destroy(uintptr_t queue) {
    if (!queue) fatal();
    if (*(volatile uint8_t *)(queue+0x46u)==0u)
        opencfw_bl_rtos_free(queue);
}
uintptr_t opencfw_boot_counting_semaphore_static(uint32_t maximum,
    uint32_t initial,uintptr_t storage) {
    if (!maximum || maximum<initial) fatal();
    uintptr_t queue=opencfw_bl_kernel_queue_create_static(maximum,0,0,storage,2);
    if (queue) *(volatile uint32_t *)(queue+0x38u)=initial;
    return queue;
}
uintptr_t opencfw_boot_counting_semaphore_dynamic(uint32_t maximum,
    uint32_t initial) {
    if (!maximum || maximum<initial) fatal();
    uintptr_t queue=opencfw_bl_kernel_queue_create_dynamic(maximum,0,2);
    if (queue) *(volatile uint32_t *)(queue+0x38u)=initial;
    return queue;
}
uintptr_t opencfw_boot_semaphore_create(uint32_t maximum,uint32_t initial,
    const uint32_t *attribute) {
    if (opencfw_bl_context_guard() || !maximum || maximum<initial) return 0;
    int32_t mode=0;
    if (attribute) mode=(attribute[2] && attribute[3]>=80)?1:
        (!attribute[2] && !attribute[3])?0:-1;
    if (mode<0) return 0;
    if (maximum!=1) return mode?opencfw_boot_counting_semaphore_static(
        maximum,initial,attribute[2]):opencfw_boot_counting_semaphore_dynamic(maximum,initial);
    uintptr_t queue=mode?opencfw_bl_kernel_queue_create_static(1,0,0,attribute[2],3):
        opencfw_bl_kernel_queue_create_dynamic(1,0,3);
    if (queue && initial && opencfw_bl_kernel_queue_put_blocking(queue,0,0,0)!=1) {
        opencfw_boot_semaphore_queue_destroy(queue);
        queue=0;
    }
    return queue;
}
