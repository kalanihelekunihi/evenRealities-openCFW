#include <stdint.h>

/* Native 0x31c0e0..0x31c41e: PHY / data-length procedure event handler
 * (record, event). Event 0x69 records the response timing (+772) and
 * signals the 0x8027f0 hook when feature bit 1 of 0x805a98 is set and the
 * procedure is idle. Events 0x0c (LL control opcode 0x802818), 0x28 and
 * 0x70 (pending masks +644/+648/+652/+656) select an opcode (0x1b or
 * 0x1c) and a step. With no procedure running (+620 = 0) the step starts
 * it through the action table 0x335300 (five actions per opcode); with
 * one running (+620 = 1) the step continues, rejects or completes it
 * (+626, +635, +631). Returns 1 once an opcode was selected. */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

typedef void (*opencfw_pcl_action)(void);
extern const opencfw_pcl_action opencfw_em9305_pcl_table_335300[10];
extern uint32_t opencfw_em9305_radio_record_timing_30c40c(uint32_t, uint32_t);
extern void opencfw_em9305_child_318d80(uintptr_t record);
extern uint32_t opencfw_em9305_phy_reject_32698c(uintptr_t, uint32_t, uint32_t);
extern uint32_t opencfw_em9305_child_31aa40(uint32_t opcode);
extern void opencfw_em9305_child_323424(uintptr_t record, uint32_t procedure);
extern uint32_t opencfw_em9305_phy_timer_start_32c7e4(uintptr_t);
extern uint32_t opencfw_em9305_child_323528(uintptr_t record, uint32_t bit);
extern uint32_t opencfw_em9305_phy_complete_32c818(uintptr_t);
extern uint32_t opencfw_em9305_phy_finish_32c810(uintptr_t);

static void pcl_action(uint32_t index, uint32_t slot, uintptr_t record)
{
    ((void (*)(uintptr_t))opencfw_em9305_pcl_table_335300[index * 5u + slot])(record);
}

uint32_t opencfw_em9305_callback_31c0e0(uintptr_t record, int32_t event)
{
    uintptr_t state = record + 635u;
    uint32_t opcode = 0x1cu;
    uint32_t step;

    if (event < 0x28) {
        if (event != 0xc)
            return 0u;
        uint32_t control = U8(0x802818u);
        if (control >= 0x23u) {
            step = 4u;
            if (control == 0x25u) {
                opcode = 0x1bu;
                step = 3u;
            } else if (control == 0x24u) {
                step = 5u;
            } else if (control != 0x23u) {
                return 0u;
            } else if (U8(state) == 0x20u || (U8(state + 13u) & 1u) != 0u) {
                (void)opencfw_em9305_phy_reject_32698c(record, 0x3au, 1u);
                return 0u;
            }
        } else {
            step = 7u;
            if (control == 7u) {
                if ((uint32_t)(U8(0x80281cu) - 0x23u) >= 3u)
                    return 0u;
            } else if (control != 0xdu && control != 0x11u) {
                return 0u;
            }
            opcode = U8(state);
            if (opcode - 0x1bu >= 2u)
                return 0u;
        }
    } else if (event == 0x28) {
        step = 0u;
    } else if (event == 0x70) {
        uint32_t high = U32(record + 656u);
        uint32_t low = U32(record + 652u);
        uint32_t flags = U32(record + 644u);
        step = (low | high) == 0u ? 1u : 2u;
        if ((flags & (1u << 27)) != 0u) {
            U32(record + 648u) = 0u;
            flags &= ~(1u << 27);
            opcode = 0x1bu;
        } else {
            if ((flags & (1u << 28)) == 0u || U8(state) == 0x20u ||
                (U32(record + 648u) & 1u) != 0u)
                return 0u;
            flags &= ~(1u << 28);
            U32(record + 648u) = 0u;
        }
        U32(record + 644u) = flags;
    } else if (event == 0x69) {
        if ((U8(0x805a98u) & 2u) == 0u || U8(state + 135u) != 1u || U8(state + 134u) != 0u)
            return 1u;
        U8(state + 137u) = (uint8_t)opencfw_em9305_radio_record_timing_30c40c(800u, U16(record + 266u));
        opencfw_em9305_child_318d80(record);
        uintptr_t hook = U32(0x8027f0u);
        if (hook != 0u)
            ((void (*)(uintptr_t))hook)(record);
        return 1u;
    } else {
        return 0u;
    }

    uint32_t index = opcode == 0x1cu;
    uint32_t running = U8(record + 620u);
    if (running == 0u) {
        if (step - 2u < 3u) {
            if (opencfw_em9305_child_31aa40(opcode) == 0u) {
                (void)opencfw_em9305_phy_reject_32698c(record, 0x1au, 0u);
                return 1u;
            }
            if (step != 2u)
                pcl_action(index, 2u, record);
            pcl_action(index, 3u, record);
            return 1u;
        }
        if (step == 0u) {
            U32(record + 636u) |= 1u << opcode;
            if (opcode != 0x1bu)
                pcl_action(index, 0u, record);
        } else if (step != 1u) {
            return 1u;
        }
        if (opencfw_em9305_child_31aa40(opcode) == 0u) {
            opencfw_em9305_child_323424(record, opcode);
            return 1u;
        }
        if (opcode == 0x1cu) {
            uint32_t pending = U32(record + 648u);
            if ((pending & 1u) != 0u) {
                uint32_t flags = U32(record + 644u);
                U32(record + 648u) = pending;
                U32(record + 644u) = flags | (1u << 28);
                return 1u;
            }
        }
        if (opcode != 0x1bu)
            pcl_action(index, 1u, record);
        (void)opencfw_em9305_phy_timer_start_32c7e4(record);
        U8(state) = (uint8_t)opcode;
        U8(record + 626u) = 1u;
        U8(record + 620u) = 1u;
        return 1u;
    }
    if (running != 1u)
        return 1u;

    switch (step) {
    case 0u:
    case 1u:
        if (opencfw_em9305_child_31aa40(opcode) == 0u) {
            opencfw_em9305_child_323424(record, opcode);
            return 1u;
        }
        if (step == 0u)
            U32(record + 636u) |= 1u << opcode;
        if (U8(state) != opcode)
            U32(record + 644u) |= 1u << opcode;
        if (step == 0u && opcode != 0x1bu)
            pcl_action(index, 0u, record);
        return 1u;
    case 3u:
        if (U8(state) == opcode)
            goto same;
        if (opencfw_em9305_child_31aa40(opcode) == 0u)
            return 1u;
        pcl_action(index, 2u, record);
        U32(record + 652u) |= 1u << opcode;
        return 1u;
    case 4u:
        pcl_action(index, 2u, record);
        if (opencfw_em9305_child_31aa40(opcode) == 0u) {
            (void)opencfw_em9305_phy_reject_32698c(record, 0x1au, 0u);
            return 1u;
        }
        if (U8(state) != 0x13u) {
            pcl_action(index, 3u, record);
            return 1u;
        }
        {
            uint32_t flags = U32(record + 644u);
            uint32_t low = U32(record + 652u);
            U32(record + 644u) = flags | (1u << opcode);
            U32(record + 652u) = low | (1u << opcode);
        }
        return 1u;
    case 5u:
        if (U8(state) != opcode) {
            uint32_t flags = U32(record + 644u);
            if ((flags & (1u << opcode)) == 0u)
                return 1u;
            uint32_t retry = U8(state - 4u);
            U32(record + 648u) = 0u;
            U32(record + 644u) = flags & ~(1u << opcode);
            if (retry != 0u)
                U8(state - 4u) = 0u;
            if (opcode != 0x1bu)
                pcl_action(index, 4u, record);
            (void)opencfw_em9305_child_323528(record, opcode);
            return 1u;
        }
    same:
        if (opcode != 0x1bu)
            pcl_action(index, 4u, record);
        (void)opencfw_em9305_child_323528(record, opcode);
        break;
    case 6u:
        (void)opencfw_em9305_child_323528(record, opcode);
        break;
    case 7u:
        opencfw_em9305_child_323424(record, opcode);
        break;
    default:
        return 1u;
    }
    (void)opencfw_em9305_phy_complete_32c818(record);
    U8(record + 626u) = 0u;
    U8(state) = 0xffu;
    U8(record + 620u) = 0u;
    (void)opencfw_em9305_phy_finish_32c810(record);
    return 1u;
}
