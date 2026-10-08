/* SPDX-License-Identifier: MIT
 * Source form of the selector at stock 0x41fadc. It applies ordered
 * register/value updates through the recovered lower 0x41d92c provider.
 * The values remain runtime inputs at their locked RAM addresses.
 */
#include "mode_publisher.h"

typedef struct {
    uint8_t register_id;
    uintptr_t value_address;
} register_update_t;

extern uint32_t opencfw_bl_power_register_update(uint32_t register_id,
                                                  uint32_t value);

#define VALUE_AT(addr_) (*(volatile const uint32_t *)(uintptr_t)(addr_))
#define UPDATE(id_, addr_) \
    { (uint8_t)(id_), (uintptr_t)(addr_) }

static const register_update_t module0_default[] = {
    UPDATE(0xc7u, 0x20000000u), UPDATE(0x40u, 0x20000004u),
    UPDATE(0x41u, 0x20000008u), UPDATE(0x48u, 0x20000024u),
};
static const register_update_t module0_pair[] = {
    UPDATE(0x42u, 0x2000000cu), UPDATE(0x43u, 0x20000010u),
};
static const register_update_t module0_group[] = {
    UPDATE(0x44u, 0x20000014u), UPDATE(0x45u, 0x20000018u),
    UPDATE(0x46u, 0x2000001cu), UPDATE(0x47u, 0x20000020u),
};
static const register_update_t module0_special[] = {
    UPDATE(0x25u, 0x20000028u), UPDATE(0x26u, 0x2000002cu),
    UPDATE(0x27u, 0x20000030u), UPDATE(0x28u, 0x20000034u),
    UPDATE(0x29u, 0x20000038u), UPDATE(0x2au, 0x2000003cu),
    UPDATE(0x2bu, 0x20000040u), UPDATE(0x2cu, 0x20000044u),
    UPDATE(0x2du, 0x20000048u),
};
static const register_update_t module1_default[] = {
    UPDATE(0x31u, 0x2000004cu), UPDATE(0x5fu, 0x20000050u),
    UPDATE(0x60u, 0x20000054u), UPDATE(0x67u, 0x20000070u),
    UPDATE(0x68u, 0x20000074u),
};
static const register_update_t module1_pair[] = {
    UPDATE(0x61u, 0x20000058u), UPDATE(0x62u, 0x2000005cu),
};
static const register_update_t module1_group[] = {
    UPDATE(0x63u, 0x20000060u), UPDATE(0x64u, 0x20000064u),
    UPDATE(0x65u, 0x20000068u), UPDATE(0x66u, 0x2000006cu),
};

static void apply_updates(const register_update_t *updates, uint32_t count)
{
    for (uint32_t i = 0u; i < count; ++i) {
        (void)opencfw_bl_power_register_update(
            updates[i].register_id, VALUE_AT(updates[i].value_address));
    }
}

#define COUNT_OF(a_) ((uint32_t)(sizeof(a_) / sizeof((a_)[0])))

void opencfw_bl_mspi_mode_publish_core(uint32_t module, uint32_t mode)
{
    /* Stock compares the full module value, then UXTBs the mode byte. */
    if (module > 1u)
        return;
    const uint8_t selector = (uint8_t)mode;

    if (module == 0u) {
        switch (selector) {
        case 0x00u:
            apply_updates(module0_default, COUNT_OF(module0_default));
            return;
        case 0x04u:
        case 0x10u:
        case 0x12u:
            apply_updates(module0_pair, COUNT_OF(module0_pair));
            apply_updates(module0_default, COUNT_OF(module0_default));
            return;
        case 0x06u:
        case 0x08u:
            apply_updates(module0_group, COUNT_OF(module0_group));
            apply_updates(module0_pair, COUNT_OF(module0_pair));
            apply_updates(module0_default, COUNT_OF(module0_default));
            return;
        case 0x0au:
            apply_updates(module0_special, COUNT_OF(module0_special));
            apply_updates(module0_group, COUNT_OF(module0_group));
            apply_updates(module0_pair, COUNT_OF(module0_pair));
            apply_updates(module0_default, COUNT_OF(module0_default));
            return;
        default:
            return;
        }
    }

    switch (selector) {
    case 0x00u:
        apply_updates(module1_default, COUNT_OF(module1_default));
        return;
    case 0x04u:
    case 0x10u:
    case 0x12u:
        apply_updates(module1_pair, COUNT_OF(module1_pair));
        apply_updates(module1_default, COUNT_OF(module1_default));
        return;
    case 0x06u:
    case 0x08u:
    case 0x16u:
    case 0x18u:
        apply_updates(module1_group, COUNT_OF(module1_group));
        apply_updates(module1_pair, COUNT_OF(module1_pair));
        apply_updates(module1_default, COUNT_OF(module1_default));
        return;
    default:
        return;
    }
}
