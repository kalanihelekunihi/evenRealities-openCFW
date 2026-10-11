/* SPDX-License-Identifier: MIT
 * Stage-2 package allocator initialization at stock 0x10006fac.
 * Native constants: 16-byte alignment, 20,884-byte zero region,
 * 20,912-byte control overhead, 1,043 twenty-byte free-list heads.
 * The source uses byte offsets because the stock layout is unusual and
 * has not been matched to a third-party allocator type.
 */
#include <stdint.h>

static uint32_t *word_at(uintptr_t address)
{
    return (uint32_t *)address;
}

void *gx8002_uart_stage2_pool_allocate_6fac(uint32_t start, uint32_t bytes)
{
    uint32_t aligned = (start + 15u) & ~UINT32_C(15);
    uint32_t delta = aligned - start;
    if (bytes < delta) return 0;
    uint32_t length = bytes - delta;
    if (length <= 31u) return 0;
    uint32_t payload = length & ~UINT32_C(15);
    if (payload <= 20911u) return 0;

    uint8_t *base = (uint8_t *)(uintptr_t)aligned;
    for (uint32_t i = 0; i < 20884u; ++i) base[i] = 0;
    *word_at((uintptr_t)base + 8u) = 20912u;
    *word_at((uintptr_t)base + 12u) = 20912u;
    uint32_t remaining = payload - 20912u;
    uintptr_t first = (uintptr_t)base + 20896u;
    uintptr_t last_size = (uintptr_t)base + payload - 8u;
    *word_at((uintptr_t)base + 20u) =
        (uint32_t)((uintptr_t)base + payload - 8u);
    *word_at((uintptr_t)base) = payload;
    *word_at((uintptr_t)base + 16u) = (uint32_t)first;
    *word_at(first) = remaining;
    *word_at(last_size) = remaining;
    for (uint32_t i = 0; i < 1043u; ++i) {
        uintptr_t head = (uintptr_t)base + 24u + i * 20u;
        *word_at(head) = 0;
        *word_at(head + 4u) = (uint32_t)head;
        *word_at(head + 8u) = 0;
        *word_at(head + 12u) = (uint32_t)head;
    }

    uint32_t bin;
    if (remaining <= 16384u) {
        bin = remaining >> 4;
    } else if ((int32_t)remaining < 0) {
        bin = 1042u;
    } else {
        uint32_t bit = remaining;
        uint32_t bit_index = 31u;
        do {
            bit <<= 1;
            --bit_index;
        } while ((int32_t)bit >= 0);
        bin = 1011u + bit_index;
    }
    uintptr_t head = (uintptr_t)base + 24u + bin * 20u;
    uintptr_t current = (uintptr_t)*word_at(head + 4u);
    while (current != head && *word_at(current) < remaining)
        current = (uintptr_t)*word_at(current + 4u);
    uintptr_t previous = (uintptr_t)*word_at(current + 12u);
    *word_at(previous + 4u) = (uint32_t)first;
    *word_at(first + remaining + 12u) = (uint32_t)previous;
    *word_at(first + 4u) = (uint32_t)current;
    *word_at(current + 12u) = (uint32_t)first;
    ++*word_at((uintptr_t)base + 40u + bin * 20u);
    return base;
}
