/* Native image-B 0x10004880..0x100048c4. Architectural IRQ entry saves
 * the exact high GPR and FPR set, dispatches the unbounded active line
 * through the RAM descriptor table, then returns with ipop/nir. These are
 * named C-SKY ISA instructions; no stock opcode array is embedded. The
 * stock disassembler labels f4ee3400/f4ee3000 as fr16-fr19, but pinned
 * binutils C-SKY FREGLIST_DASH syntax assembles the same save/restore
 * instructions with fr0-fr7 on CK804EF (also observed in image A).
 */
#include <stdint.h>

extern volatile uint32_t gx8002_image_b_irq_descriptors_200173a8[];

__attribute__((used)) static void gx8002_image_b_irq_dispatch_source(void)
{
    volatile uint32_t *const controller =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0xe000ec00);
    uint32_t line = (controller[0] & UINT32_C(511)) - 32u;
    uintptr_t descriptor =
        (uintptr_t)gx8002_image_b_irq_descriptors_200173a8 + line * 8u;
    uint32_t callback = *(volatile uint32_t *)descriptor;
    if (callback != 0u) {
        uint32_t argument = *(volatile uint32_t *)(descriptor + 4u);
        ((void (*)(uint32_t, uint32_t))(uintptr_t)callback)(line, argument);
    }
}

__attribute__((naked, used))
void gx8002_image_b_generic_irq_10004880(void)
{
    __asm__ volatile(
        "nie\n"
        "ipush\n"
        "subi r14, r14, 56\n"
        "stm r18-r31, (r14)\n"
        "subi r14, r14, 32\n"
        "fstms fr0-fr7, (r14)\n"
        "push r15\n"
        "bsr gx8002_image_b_irq_dispatch_source\n"
        "ld.w r15, (r14, 0x0)\n"
        "addi r14, r14, 4\n"
        "fldms fr0-fr7, (r14)\n"
        "addi r14, r14, 32\n"
        "ldm r18-r31, (r14)\n"
        "addi r14, r14, 56\n"
        "ipop\n"
        "nir\n"
    );
}
