/* Native QK_onIdle0x3115e4..0x31161c. ILINK is hardware state,
 * callback R0 is its own address, and sleep-return R0 feeds SETI.
 */
#include <stdint.h>
extern uint32_t opencfw_em9305_sleep_lower(uint32_t irq_state,uint32_t ilink); /* 0x3126e0 */
void opencfw_em9305_idle(void)
{
    __asm__ volatile("mov ilink,0" ::: "r29","memory");
    uintptr_t callback = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x80fe18);
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    callback = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x80fe14);
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    uint32_t irq;
    __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
    uint32_t link;
    __asm__ volatile("mov %0,ilink" : "=r"(link) :: "memory");
    if (link == 0) irq = opencfw_em9305_sleep_lower(irq,link);
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
}
