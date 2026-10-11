/* Bounded source trace fixture; no peripheral or original-byte execution. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern int32_t gx8002_image_b_audio_irq_10015830(int32_t irq, void *private_data);

static uint32_t enabled, pending;
static uint32_t callback_flags[4], callback_count[4];
static uint32_t callback_addresses[2][3];
static uint32_t ack[11], ack_count;
static uint32_t callback_order[4], callback_order_count;
static uint32_t read_order[64], read_order_count;

uint32_t gx8002_image_b_isr_test_read(uint32_t offset)
{
    if (read_order_count >= 64u) __builtin_trap();
    read_order[read_order_count++] = offset;
    if (offset == 0x100u) return enabled;
    if (offset == 0x104u) return pending;
    if (offset == 0x124u) return 0x124u;
    if (offset == 0x148u) return 0x148u;
    if (offset == 0x168u) return 0x168u;
    if (offset == 0x128u) return 0x128u;
    if (offset == 0x14cu) return 0x14cu;
    if (offset == 0x16cu) return 0x16cu;
    fprintf(stderr, "unexpected IRQ read %x\n", offset);
    __builtin_trap();
}

void gx8002_image_b_isr_test_write(uint32_t offset, uint32_t value)
{
    if (offset != 0x104u || ack_count >= 11u) __builtin_trap();
    ack[ack_count++] = value;
    pending &= ~value;
}

void gx8002_image_b_isr_test_event(uint32_t slot, uint32_t flags)
{
    unsigned index = slot == 0x14u ? 0u : 3u;
    if (slot != 0x14u && slot != 0x18u) __builtin_trap();
    callback_flags[index] = flags;
    callback_count[index]++;
    callback_order[callback_order_count++] = slot;
}

void gx8002_image_b_isr_test_stream(uint32_t slot, uint32_t flags,
                                     uint32_t address[3])
{
    unsigned index = slot == 0x0cu ? 1u : 2u;
    if (slot != 0x0cu && slot != 0x10u) __builtin_trap();
    callback_flags[index] = flags;
    callback_count[index]++;
    memcpy(callback_addresses[index - 1u], address, 3u * sizeof(uint32_t));
    callback_order[callback_order_count++] = slot;
}

static unsigned fail(unsigned case_number, const char *why)
{
    fprintf(stderr, "case %u: %s\n", case_number, why);
    return 1u;
}

int main(void)
{
    static const unsigned bits[11] = {0, 1, 2, 3, 4, 5, 16, 17, 18, 19, 20};
    for (unsigned n = 0; n < 8192; ++n) {
        enabled = pending = 0u;
        for (unsigned i = 0; i < 11; ++i) {
            if ((n >> i) & 1u) enabled |= 1u << bits[i];
            if (((n * 37u + 11u) >> i) & 1u) pending |= 1u << bits[i];
        }
        uint32_t active = enabled & pending;
        memset(callback_flags, 0, sizeof(callback_flags));
        memset(callback_count, 0, sizeof(callback_count));
        memset(callback_addresses, 0, sizeof(callback_addresses));
        memset(ack, 0, sizeof(ack));
        memset(callback_order, 0, sizeof(callback_order));
        ack_count = callback_order_count = 0u;
        read_order_count = 0u;
        if (gx8002_image_b_audio_irq_10015830(2, 0) != 0)
            return fail(n, "IRQ return status");
        uint32_t expected[4] = {
            (active >> 18) & 7u,
            active & 7u,
            (active >> 3) & 7u,
            (active >> 16) & 3u,
        };
        for (unsigned i = 0; i < 4; ++i) {
            if (callback_flags[i] != expected[i]) return fail(n, "callback mask");
            if (callback_count[i] != (expected[i] != 0u || i == 3u))
                return fail(n, "callback count");
        }
        unsigned expected_order[4] = {0x14u, 0x0cu, 0x10u, 0x18u};
        unsigned order_length = 0u;
        for (unsigned i = 0; i < 4; ++i)
            if (expected[i] != 0u || i == 3u)
                if (callback_order[order_length++] != expected_order[i])
                    return fail(n, "callback order");
        if (callback_order_count != order_length) return fail(n, "callback order length");
        if (expected[1] != 0u &&
            (callback_addresses[0][0] != 0x124u ||
             callback_addresses[0][1] != 0x148u ||
             callback_addresses[0][2] != 0x168u)) return fail(n, "record addresses");
        if (expected[2] != 0u) {
            if (((expected[2] & 1u) && callback_addresses[1][0] != 0x128u) ||
                ((expected[2] & 2u) && callback_addresses[1][1] != 0x14cu) ||
                ((expected[2] & 4u) && callback_addresses[1][2] != 0x16cu))
                return fail(n, "update addresses");
        }
        unsigned expected_acks[] = {18, 19, 20, 0, 1, 2, 3, 4, 5, 16, 17};
        unsigned count = 0u;
        for (unsigned i = 0; i < 11; ++i)
            if ((active >> expected_acks[i]) & 1u)
                if (ack[count++] != (1u << expected_acks[i]))
                    return fail(n, "ack order");
        if (ack_count != count || (pending & active) != 0u)
            return fail(n, "ack count/status");
    }
    enabled = pending = 0u;
    read_order_count = 0u;
    (void)gx8002_image_b_audio_irq_10015830(2, 0);
    static const uint32_t native_quiet_reads[] = {
        0x104u, 0x104u, 0x104u,
        0x100u, 0x100u, 0x100u,
        0x100u, 0x124u, 0x100u, 0x148u, 0x100u, 0x168u,
        0x100u, 0x100u, 0x100u,
        0x100u, 0x100u,
    };
    if (read_order_count != sizeof(native_quiet_reads) / sizeof(native_quiet_reads[0]) ||
        memcmp(read_order, native_quiet_reads, sizeof(native_quiet_reads)) != 0)
        return fail(8192u, "quiet-path native read order");
    puts("8192 bounded IRQ callback/W1C traces and quiet-path reads pass");
    return 0;
}
