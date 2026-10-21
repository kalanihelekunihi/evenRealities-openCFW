/* Native QF_onResume0x3110f4..0x31114c and QF_resume0x311218..0x311230.
 * Product callback slots and controller root retain authenticated identities.
 */
#include <stdint.h>
extern void opencfw_em9305_idle(void);
void opencfw_em9305_resume_hook(void)
{
    volatile uint32_t *const registers = (volatile uint32_t *)(uintptr_t)UINT32_C(0xf00a74);
    registers[0] = 3;
    uintptr_t callback = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x80fe08);
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    callback = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x80fe04);
    if (callback != 0) ((void (*)(uintptr_t))callback)(callback);
    const uintptr_t controller = *(volatile uint32_t *)(uintptr_t)UINT32_C(0x801090);
    if (controller != 0) {
        const uintptr_t handler = *(volatile uint32_t *)(controller + 12u);
        if (handler != 0) ((void (*)(uint32_t))handler)(0);
    }
    uint32_t irq;
    __asm__ volatile("clri %0\n\tsync" : "=r"(irq) :: "memory");
    volatile uint8_t *const nesting = (volatile uint8_t *)(uintptr_t)UINT32_C(0x801398);
    if (*nesting != 0) { const uint8_t old = *nesting; *nesting = (uint8_t)(old - 1u); }
    registers[3] = 1;
    __asm__ volatile("seti %0" :: "r"(irq) : "memory");
}
_Noreturn void opencfw_em9305_framework_resume(void)
{
    __asm__ volatile("clri 0\n\tsync" ::: "memory");
    opencfw_em9305_resume_hook();
    __asm__ volatile("seti 0" ::: "memory");
    for (;;) opencfw_em9305_idle();
}
