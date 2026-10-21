/* SPDX-License-Identifier: MIT
 * Source reconstruction of locked bootloader routine 0x426808.
 *
 * The register-save layout and operation ordering follow the locked-image
 * decompilation at g2/research/corpus/apollo-bootloader/ghidra/open-2026-09-29/
 * decomp/00426808.c. The public Apollo510 5.1.0 source copy is documented in
 * the upstream-worker provenance report; its am_hal_mspi_power_control()
 * confirms the same save/restore register family, with a different state ABI.
 * Hardware helpers are explicit callouts so synthetic tests cannot access
 * physical peripherals.
 */
#include "power_control.h"

#define HANDLE_MAGIC_MASK 0x01ffffffu
#define HANDLE_MAGIC      0x01bebebeu
#define SAVE_VALID_BYTE   0x860u /* byte address of handle word 0x218 */
#define XIP_DELAY_WORD    0x233u
#define ACTIVE_COUNT_WORD 0x210u
#define BUSY_WORD         8u
#define CLOCK_CLASS_BYTE  0x8c9u

typedef struct {
    uint16_t reg;
    uint16_t word;
} saved_reg_t;

/* This order is the order of the stock loads/stores. The gap at state word
 * 0x228 is intentional: it contains CQCFG, followed by CQADDR at 0x229. */
static const saved_reg_t save_order[] = {
    {0x080u, 0x219u}, {0x084u, 0x21au}, {0x088u, 0x21bu},
    {0x08cu, 0x21cu}, {0x090u, 0x21du}, {0x094u, 0x21eu},
    {0x098u, 0x21fu}, {0x09cu, 0x220u}, {0x0a0u, 0x221u},
    {0x0a4u, 0x222u}, {0x0a8u, 0x223u}, {0x030u, 0x224u},
    {0x044u, 0x225u}, {0x048u, 0x226u}, {0x04cu, 0x227u},
    {0x2a8u, 0x229u}, {0x2b8u, 0x22au}, {0x2c0u, 0x22bu},
    {0x2c4u, 0x22cu}, {0x200u, 0x22du}, {0x2b0u, 0x22eu},
    {0x114u, 0x22fu}, {0x118u, 0x230u}, {0x020u, 0x231u},
    {0x2a0u, 0x228u}
};

static uint8_t user_id(const uint32_t *handle)
{
    return (uint8_t)(handle[1] + 0x10u);
}

static uint32_t valid_handle(const uint32_t *handle)
{
    return handle != 0 && (handle[0] & HANDLE_MAGIC_MASK) == HANDLE_MAGIC;
}

static void save_registers(uint32_t *handle,
                           const opencfw_mspi_power_ops_t *ops,
                           uint32_t module)
{
    for (uint32_t i = 0; i < sizeof(save_order) / sizeof(save_order[0]); ++i)
        handle[save_order[i].word] = ops->mmio_read(module, save_order[i].reg);
}

static void restore_registers(uint32_t *handle,
                              const opencfw_mspi_power_ops_t *ops,
                              uint32_t module)
{
    for (uint32_t i = 0; i < sizeof(save_order) / sizeof(save_order[0]); ++i) {
        const saved_reg_t item = save_order[i];
        uint32_t value = handle[item.word];
        if (item.word == 0x228u)
            value &= ~1u;
        if (item.word == 0x22eu)
            value = (uint8_t)value;
        /* Stock saves CQFLAGS at 0x2b0 and restores them through CQSETCLEAR
         * at 0x2b4; every other pair uses its source register offset. */
        const uint16_t reg = item.word == 0x22eu ? 0x2b4u : item.reg;
        ops->mmio_write(module, reg, value);
    }
}

uint32_t opencfw_hal_mspi_power_control(uint32_t *handle,
                                        uint32_t operation,
                                        uint32_t retain_state,
                                        const opencfw_mspi_power_ops_t *ops)
{
    if (!valid_handle(handle))
        return 2u;

    /* The entry takes byte/char arguments in the image; preserve their
     * truncation before branch tests and helper calls. */
    const uint8_t op = (uint8_t)operation;
    const uint8_t retain = (uint8_t)retain_state;
    const uint32_t module = handle[1];
    const uint8_t user = user_id(handle);

    if (op == 0u) {
        if (retain != 0u && ((volatile uint8_t *)handle)[SAVE_VALID_BYTE] == 0u)
            return 7u;

        (void)ops->mode_enter(user);
        if (retain == 0u) {
            ((volatile uint8_t *)handle)[CLOCK_CLASS_BYTE] = 4u;
            const uint32_t status = ops->clock_request(4u, user);
            if (status != 0u)
                return status;
            ops->clockgen(module, 1u, 1u, 8u);
        } else {
            const uint8_t clock_class =
                ((volatile uint8_t *)handle)[CLOCK_CLASS_BYTE];
            if (clock_class == 7u)
                return 7u;
            const uint32_t status = ops->clock_request(clock_class, user);
            if (status != 0u)
                return status;
            ops->clockgen(module, 1u, 0u, 0u);
            restore_registers(handle, ops, module);
            if ((uint8_t)handle[0x228u] & 1u)
                (void)ops->cq_enable(handle);
            ((volatile uint8_t *)handle)[SAVE_VALID_BYTE] = 0u;
        }
        return 0u;
    }

    if (op > 2u)
        return 6u;
    if (handle[ACTIVE_COUNT_WORD] != 0u || handle[BUSY_WORD] != 0u)
        return 3u;

    if (retain != 0u) {
        save_registers(handle, ops, module);
        if (ops->mmio_read(module, 0x2a0u) & 1u)
            (void)ops->cq_disable(handle);
        ((volatile uint8_t *)handle)[SAVE_VALID_BYTE] = 1u;
    }

    (void)ops->interrupt_disable(handle, 0x1fffu);
    if (ops->mmio_read(module, 0x090u) & 1u)
        ops->delay_us(handle[XIP_DELAY_WORD]);
    (void)ops->mode_leave(user);
    ops->clockgen(module, 0u, 0u, 0u);
    return ops->clock_release_all(user);
}
