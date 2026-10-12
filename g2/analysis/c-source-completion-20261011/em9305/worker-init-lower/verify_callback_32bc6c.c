#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

extern uint32_t opencfw_em9305_callback_32bc6c(uint32_t record,
                                                  uint32_t packet);

static uint32_t decoder_return;
static uint32_t decoder_calls;
static uint32_t child_calls;
static uint32_t observed_packet;
static uint32_t observed_mode;
static uint32_t observed_code;

uint32_t opencfw_em9305_child_3191dc(uint32_t context, uint32_t packet,
                                      uint32_t mode)
{
    assert(context == 0x802810u);
    decoder_calls++;
    observed_packet = packet;
    observed_mode = mode;
    return decoder_return;
}

uint32_t opencfw_em9305_child_32a000(uint32_t packet, uint32_t code)
{
    child_calls++;
    observed_packet = packet;
    observed_code = code;
    return 0xabc00000u | code;
}

int main(void)
{
    static uint8_t record[4] = {0};
    uint32_t pointer = (uint32_t)(uintptr_t)record;
    assert(opencfw_em9305_callback_32bc6c(pointer, 0x12345678u) == 0u);
    assert(decoder_calls == 0u && child_calls == 0u);

    record[0] = 1;
    record[2] = 0xd7;
    const uint32_t returns[] = {0x1eu, 0u, 1u, 0xffffffffu};
    const uint32_t codes[] = {0xeu, 0xcu, 0xdu, 0xdu};
    for (unsigned i = 0; i < 4; ++i) {
        decoder_return = returns[i];
        uint32_t actual = opencfw_em9305_callback_32bc6c(pointer,
                                                             0x12345678u);
        assert(actual == (0xabc00000u | codes[i]));
        assert(observed_packet == pointer);
        assert(observed_mode == 0xd7u);
        assert(observed_code == codes[i]);
    }
    assert(decoder_calls == 4u && child_calls == 4u);
    puts("32bc6c callback: zero + four result routes PASS");
    return 0;
}
