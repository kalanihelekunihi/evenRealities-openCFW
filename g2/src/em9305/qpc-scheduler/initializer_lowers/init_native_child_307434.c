#include <stdint.h>

/* Native 0x307434..0x307478: is LL procedure (opcode 0x15..0x23, mask 0x7ccf)
 * pending or active on the connection? Looks up the procedure's slot in the
 * ROM table at 0x334479 and compares it with the active procedure byte +635
 * and the pending bitmap +644 of the 912-byte connection entry. */
extern const uint8_t opencfw_em9305_proc_pending_334479[15];

uint32_t opencfw_em9305_child_307434(uint32_t handle, uint32_t opcode)
{
    uint32_t index = opcode - 0x15u;
    if (index > 14u) return 0u;
    if (((0x7ccfu >> index) & 1u) == 0u) return 0u;
    uintptr_t entry = *(volatile uint32_t *)(uintptr_t)0x805c70u + (handle & 0xffffu) * 912u;
    uint32_t slot = opencfw_em9305_proc_pending_334479[index];
    if (*(volatile uint8_t *)(entry + 635u) == slot) return 1u;
    return (*(volatile uint32_t *)(entry + 644u) >> (slot & 31u)) & 1u;
}
