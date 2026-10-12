#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

/* A connected switch fragment for native 0x3191dc's 43-row dispatch.
 * This is deliberately not the public 0x3191dc provider: false means
 * another native route still needs source, and no success is fabricated.
 * In native call ABI: r0=context, r1=payload, r2=mode. */
static uint8_t read8(uintptr_t address)
{ return *(volatile const uint8_t *)address; }
static void write8(uintptr_t address, uint8_t value)
{ *(volatile uint8_t *)address = value; }
static uint32_t status_for_state(uint8_t observed, uint8_t expected)
{ return observed == expected ? 0u : 25u; }
static uint32_t expected_state(uintptr_t context, uint8_t state)
{ return status_for_state(read8(context + 5u), state); }
static uint32_t read32(uintptr_t address)
{ return *(volatile const uint32_t *)address; }
static uint16_t read16(uintptr_t address)
{ return *(volatile const uint16_t *)address; }

extern uint32_t opencfw_em9305_packet_child_32dbe4(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32dc40(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32dd20(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32de08(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32deac(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32dfe8(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32dffc(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32e068(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32e114(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32e128(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32e1f4(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32dba4(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_packet_child_32de6c(uint32_t fields, uintptr_t payload, uint32_t third);
extern uint32_t opencfw_em9305_ll_mask_count_30c414(uint32_t low, uint32_t high);

bool opencfw_em9305_packet_switch_known(uint8_t opcode, uintptr_t context,
                                        uintptr_t payload, uint32_t mode,
                                        uint32_t *status)
{
    switch (opcode) {
    case 0: { /* Native 0x31936c..0x3193d8. */
        if (mode == 0u) { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32de6c((uint32_t)(context + 12u), payload, mode);
        if (read8(context + 5u) != 12u) { *status = 25u; return true; }
        uint32_t first = read16(context + 16u);
        uint32_t first_adjusted = (uint16_t)(first - 3201u);
        if (first_adjusted < 0xf385u) { *status = 30u; return true; }
        uint32_t payload_count = read8(context + 12u);
        if (payload_count == 0u || payload_count >= (first < 9u ? first : 9u) ||
            first < read16(context + 14u))
            { *status = 30u; return true; }
        uint32_t budget = read16(context + 20u);
        uint32_t budget_adjusted = (uint16_t)(budget - 3201u);
        if (budget_adjusted < 0xf389u) { *status = 30u; return true; }
        uint32_t period = read16(context + 18u);
        /* ARC MPYWHUL multiplies the full first word by the low half of
         * the second, returning low 32 bits. Both operands are halfwords. */
        uint32_t product = (period + 1u) * first;
        *status = (int32_t)product < (int32_t)(budget << 2u) && period < 500u ? 0u : 30u;
        return true;
    }
    case 1: { /* Native 0x319268..0x319298. */
        if (mode == 0u) { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dba4((uint32_t)(context + 12u), payload, mode);
        if (read8(context + 5u) != 8u) { *status = 25u; return true; }
        uint32_t high = read32(context + 16u);
        if (high >= 32u) { *status = 30u; return true; }
        uint32_t low = read32(context + 12u);
        *status = opencfw_em9305_ll_mask_count_30c414(low, high) >= 2u ? 0u : 30u;
        return true;
    }
    case 3: case 4: case 5: case 6: case 10: case 11: case 18: case 19:
        *status = 25u; return true; /* Native 0x319204. */
    case 2: case 7: { /* Native 0x3196ec/0x319700. */
        uint8_t observed = read8(context + 5u);
        write8(context + 12u, read8(payload + 1u));
        *status = status_for_state(observed, 2u); return true;
    }
    case 17: { /* Native 0x319620. */
        if ((read8(0x805a94u) & 4u) == 0u) { *status = 25u; return true; }
        uint8_t first = read8(payload + 1u);
        uint8_t observed = read8(context + 5u);
        write8(context + 12u, first);
        write8(context + 13u, read8(payload + 2u));
        *status = status_for_state(observed, 3u); return true;
    }
    case 9: /* Native 0x319420. */
        (void)opencfw_em9305_packet_child_32dfe8((uint32_t)(context + 12u), payload, mode);
        *status = expected_state(context, 9u); return true;
    case 12: /* Native 0x3191c4. */
        (void)opencfw_em9305_packet_child_32e1f4((uint32_t)(context + 12u), payload, mode);
        *status = expected_state(context, 6u); return true;
    case 13: /* Native 0x3191ac; final store is return delay slot. */
        write8(context + 12u, 255u);
        uint8_t observed = read8(context + 5u);
        *status = status_for_state(observed, 2u);
        write8(context + 13u, read8(payload + 1u));
        return true;
    case 8: /* Native 0x319414: mode-zero early return, else 0x319420. */
        if (mode == 0u) { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dfe8((uint32_t)(context + 12u), payload, mode);
        *status = expected_state(context, 9u); return true;
    case 14: { /* Native 0x3194cc. */
        if (mode == 1u) { *status = 25u; return true; }
        uint32_t fresh_flag = read8(0x805a94u);
        if ((fresh_flag & 8u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dfe8((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 9u); return true;
    }
    case 15: case 16: { /* Native 0x319338/0x31935c. */
        if (opcode == 16u && mode == 1u) { *status = 25u; return true; }
        uint32_t fresh_flag = read8(0x805a94u);
        if ((fresh_flag & 2u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32de08((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 24u); return true;
    }
    case 20: case 21: /* Native 0x319438. */
        (void)opencfw_em9305_packet_child_32deac((uint32_t)(context + 12u), payload, mode);
        *status = expected_state(context, 9u); return true;
    case 22: case 23: { /* Native 0x31953c/0x319564. */
        if (opcode == 23u && mode == 1u) { *status = 25u; return true; }
        uint32_t fresh_flag = read8(0x805a95u);
        if ((fresh_flag & 9u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32e114((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 3u); return true;
    }
    case 24: { /* Native 0x319574. */
        if (mode == 0u) { *status = 25u; return true; }
        uint32_t fresh_flag = read8(0x805a95u);
        if ((fresh_flag & 9u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32e128((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 5u); return true;
    }
    case 25: { /* Native 0x319450. */
        if (mode == 1u || (read8(0x805a96u) & 1u) == 0u)
            { *status = 25u; return true; }
        uint8_t first = read8(payload + 1u);
        uint8_t masked = (uint8_t)(first & 7u);
        uint8_t observed = read8(context + 5u);
        write8(context + 12u, first);
        write8(context + 12u, masked);
        uint8_t second = read8(payload + 2u);
        write8(context + 13u, second);
        if (observed != 3u) { *status = 25u; return true; }
        if (masked == 0u) { *status = 30u; return true; }
        uint32_t shifted = (uint8_t)(second - 0x26u);
        *status = shifted > 219u ? 0u : 30u;
        return true;
    }
    case 28: { /* Native 0x3194f4. */
        uint32_t fresh_flag = read8(0x805a97u);
        if ((fresh_flag & 2u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dffc((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 35u); return true;
    }
    case 31: { /* Native 0x3192c0. */
        if (mode == 0u) { *status = 25u; return true; }
        uint32_t fresh_flag = read32(0x805a94u);
        if ((fresh_flag & (1u << 29)) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dc40((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 36u); return true;
    }
    case 32: { /* Native 0x3192e8. */
        if (mode == 1u) { *status = 25u; return true; }
        uint32_t fresh_flag = read32(0x805a94u);
        if ((fresh_flag & (1u << 28)) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dd20((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 9u); return true;
    }
    case 33: { /* Native 0x319298. */
        if (mode == 0u) { *status = 25u; return true; }
        uint32_t fresh_flag = read32(0x805a94u);
        if ((fresh_flag & (1u << 29)) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32dbe4((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 16u); return true;
    }
    case 42: { /* Native 0x319518. */
        uint32_t fresh_flag = read8(0x805a97u);
        if ((fresh_flag & 2u) == 0u)
            { *status = 25u; return true; }
        (void)opencfw_em9305_packet_child_32e068((uint32_t)(context + 12u), payload, fresh_flag);
        *status = expected_state(context, 43u); return true;
    }
    case 38: case 39: { /* Native 0x319698/0x319644. */
        if ((opcode == 38u ? mode == 1u : mode == 0u) ||
            (read8(0x805a98u) & 32u) == 0u)
            { *status = 25u; return true; }
        uint8_t observed = 0u;
        for (uint32_t i = 0; i < 5u; ++i) {
            uint8_t hi = read8(payload + 2u + 2u * i);
            uint8_t lo = read8(payload + 1u + 2u * i);
            *(volatile uint16_t *)(context + 12u + 2u * i) =
                (uint16_t)(lo | ((uint16_t)hi << 8));
            if (i == 1u) observed = read8(context + 5u);
        }
        *status = status_for_state(observed, 11u); return true;
    }
    case 40: { /* Native 0x319208. */
        if (mode == 0u || (read8(0x805a98u) & 128u) == 0u)
            { *status = 25u; return true; }
        uint8_t first = read8(payload + 1u);
        uint8_t observed = read8(context + 5u);
        write8(context + 12u, first);
        write8(context + 13u, read8(payload + 2u));
        write8(context + 14u, read8(payload + 3u));
        *status = status_for_state(observed, 4u); return true;
    }
    case 41: /* Native 0x319234; AW pre-load and AB post-store. */
        if (mode == 1u || (read8(0x805a98u) & 128u) == 0u)
            { *status = 25u; return true; }
        for (uint32_t i = 0; i < 10u; ++i)
            write8(context + 12u + i, read8(payload + 1u + i));
        *status = expected_state(context, 11u); return true;
    case 26: { /* Native 0x3193d8. */
        if ((read8(0x805a96u) & 4u) == 0u) { *status = 25u; return true; }
        uint8_t value = read8(payload + 1u);
        uint8_t observed = read8(context + 5u);
        write8(context + 13u, (uint8_t)(value >> 6));
        write8(context + 12u, (uint8_t)(value & 31u));
        *status = status_for_state(observed, 2u); return true;
    }
    case 27: /* Native 0x319400. */
        *status = (read8(0x805a96u) & 2u) != 0u ? 0u : 25u; return true;
    case 29: case 30: { /* Native 0x31948c/0x3194ac. */
        if ((read8(0x805a97u) & 4u) == 0u) { *status = 25u; return true; }
        uint8_t observed = read8(context + 5u);
        write8(context + 12u, read8(payload + 1u));
        *status = status_for_state(observed, 2u); return true;
    }
    case 34: { /* Native 0x319310. */
        if ((read8(0x805a97u) & 0x30u) == 0u) { *status = 25u; return true; }
        write8(context + 12u, read8(payload + 1u));
        uint8_t second = read8(payload + 2u);
        uint8_t observed = read8(context + 5u);
        write8(context + 13u, second);
        write8(context + 14u, read8(payload + 3u));
        *status = status_for_state(observed, 4u); return true;
    }
    case 35: { /* Native 0x3195cc. */
        if ((read8(0x805a98u) & 2u) == 0u) { *status = 25u; return true; }
        write8(context + 12u, read8(payload + 1u));
        uint8_t second = read8(payload + 2u);
        uint8_t observed = read8(context + 5u);
        write8(context + 13u, second);
        write8(context + 14u, read8(payload + 3u));
        *status = status_for_state(observed, 4u); return true;
    }
    case 36: case 37: { /* Native 0x3195f4/0x3195a0. */
        if ((read8(0x805a98u) & (opcode == 36u ? 2u : 4u)) == 0u)
            { *status = 25u; return true; }
        write8(context + 12u, read8(payload + 1u));
        write8(context + 13u, read8(payload + 2u));
        uint8_t third = read8(payload + 3u);
        uint8_t observed = read8(context + 5u);
        write8(context + 14u, third);
        write8(context + 15u, read8(payload + 4u));
        *status = status_for_state(observed, 5u); return true;
    }
    default:
        return false;
    }
}
