#define _GNU_SOURCE
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include "init_lower_native.h"

#define CB(name) void opencfw_em9305_callback_##name(void) {}
CB(32483c) CB(317f5c) CB(317ca8) CB(31ce50)
CB(31f9b0) CB(319890) CB(31fa44)
CB(31ff68) CB(320434) CB(322a30)
CB(31e7fc) CB(318c1c) CB(318f2c) CB(3189f4) CB(31df8c)
CB(31bd78) CB(320f78) CB(322754) CB(325984)

static unsigned fill_calls;
static unsigned calls_303d18, calls_302ec8;
static unsigned calls_303008, calls_302ff4, calls_30e42c;
uint32_t opencfw_em9305_common_init_303008(uint32_t incoming) {
    assert(incoming == 0x01020304u);
    ++calls_303008;
    return 0x11111111u;
}
uint32_t opencfw_em9305_common_init_302ff4(uint32_t incoming) {
    assert(incoming == 0x11111111u && calls_303008 == calls_302ff4 + 1u);
    ++calls_302ff4;
    return 0x22222222u;
}
uint32_t opencfw_em9305_init_lower_30e42c(uint32_t incoming) {
    assert(incoming == 0x809000u && calls_302ff4 == calls_30e42c + 1u);
    ++calls_30e42c;
    return 0x00010001u;
}
uint32_t opencfw_em9305_common_init_303d18(uint32_t incoming) {
    assert(incoming == 0x55331177u);
    ++calls_303d18;
    return 10u;
}
uint32_t opencfw_em9305_common_init_302ec8(void) {
    assert(calls_303d18 == calls_302ec8 + 1u);
    ++calls_302ec8;
    return 11u;
}
void *opencfw_em9305_memset(void *destination, uint32_t value, uint32_t bytes) {
    ++fill_calls;
    return memset(destination, (int)(uint8_t)value, bytes);
}

extern uint32_t opencfw_em9305_init_lower_306c44(uint32_t);
extern uint32_t opencfw_em9305_init_lower_3077f4(uint32_t);
extern uint32_t opencfw_em9305_init_lower_307834(uint32_t);
extern uint32_t opencfw_em9305_init_lower_3079c4(uint32_t);
extern uint32_t opencfw_em9305_init_lower_307af8(uint32_t);

int main(void) {
    void *base = mmap((void *)0x800000u, 0x10000u, PROT_READ | PROT_WRITE,
                      MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    assert(base == (void *)0x800000u);
    void *table = mmap((void *)0x330000u, 0x10000u, PROT_READ | PROT_WRITE,
                       MAP_PRIVATE | MAP_ANONYMOUS | MAP_FIXED, -1, 0);
    assert(table == (void *)0x330000u);
    init_write32(0x3357a8u, 0x802d20u);
    init_write32(0x3357acu, 0x802fe0u);
    init_write32(0x3357b0u, 0x8032a0u);
    init_write32(0x3357b4u, 0x8035dcu);
    init_write32(0x3357b8u, 0x802a60u);
    init_write32(0x3357bcu, 0x80389cu);
    init_write32(0x803b5cu, 0x12345678u);
    init_write32(0x803b60u, 0xabcdef01u);
    init_write32(0x803b64u, 0x13579bdfu);
    *(volatile uint8_t *)0x802d20u = 1u;
    *(volatile uint8_t *)0x8035dcu = 0u;
    assert(opencfw_em9305_callback_307a18(0u) == 1u);
    assert(opencfw_em9305_callback_307b60(0u) == 0u);
    init_write32(0x805cacu, 0x805d00u);
    init_write32(0x805c40u, 0x807000u);
    init_write32(0x805c3cu, 0x808000u);
    init_write32(0x805c70u, 0x809000u);
    *(volatile uint8_t *)0x805d22u = 1u;
    *(volatile uint8_t *)0x805d3au = 2u;
    *(volatile uint8_t *)0x805d39u = 1u;
    for (unsigned version = 0; version != 256; ++version) {
        *(volatile uint8_t *)0x805d04u = (uint8_t)version;
        init_write32(0x805b30u, 0x80000000u);
        init_write32(0x805b34u, 0x12340000u);
        uint32_t a = opencfw_em9305_init_lower_306c44(version);
        assert(a == 0x12340020u && init_read32(0x805b34u) == a);
        assert(init_read32(0x8056a4u) == init_code_address(opencfw_em9305_callback_32483c));
        uint32_t b = opencfw_em9305_init_lower_3077f4(version);
        assert(b == (version < 11u ? version : 0x805b30u));
        assert(init_read32(0x805b30u) == 0x80000000u);
        assert(init_read8(0x807000u) == 0u && init_read8(0x8073ffu) == 0u);
        assert(init_read8(0x808000u) == 0u && init_read8(0x8081ffu) == 0u);
        uint32_t c = opencfw_em9305_init_lower_307834(version);
        assert(init_read8(0x8027ccu) == 1u);
        assert(init_read32(0x8027d0u) == init_code_address(opencfw_em9305_callback_3189f4));
        assert(init_read8(0x809000u) == 0u && init_read8(0x80938fu) == 0u);
        uint32_t prior = 0x80000000u;
        if (version == 7u) prior |= 0xeu;
        else if (version == 8u) prior |= 0x2eu;
        else if (version == 9u) prior |= 0x1002eu;
        else if (version >= 10u) prior |= 0x501002eu;
        assert(c == (prior | (version < 7u ? 1u : 0x11u)));
        assert(init_read32(0x805b30u) == c);
        uint32_t d = opencfw_em9305_init_lower_3079c4(version);
        assert(d == 704u && *(volatile uint16_t *)0x805b20u == 704u);
        assert(init_read32(0x801304u) == (uint32_t)(uintptr_t)opencfw_em9305_callback_307a18);
        assert(init_read8(0x802d30u) == 0u);
        assert(init_read8(0x802ff0u) == 1u);
        assert(init_read8(0x8032b0u) == 2u);
        uint32_t e = opencfw_em9305_init_lower_307af8(version);
        assert(e == 0x805b0cu && *(volatile uint16_t *)0x805b1eu == 704u);
        assert(init_read32(0x801308u) == (uint32_t)(uintptr_t)opencfw_em9305_callback_307b60);
        assert(init_read8(0x8035ecu) == 0u);
        assert(init_read8(0x802a70u) == 1u);
        assert(init_read8(0x8038acu) == 2u);
        assert(init_read32(0x803670u) == 0x12345678u);
        assert(init_read32(0x802af4u) == 0xabcdef01u);
        assert(init_read32(0x803930u) == 0x13579bdfu);
        assert(init_read32(0x805b34u) == (0x12340020u | (version >= 12u ? 0x80u : 0u) | (version >= 14u ? 0x400u : 0u)));
    }
    assert(fill_calls == 256u * 10u);
    assert(opencfw_em9305_callback_30fc20(0x12345678u, 3u) == 0x12345678u);
    assert(init_read32(0x805eb8u) == 0x12345678u && init_read8(0x805ebcu) == 3u);
    assert(opencfw_em9305_callback_30fc24(0x87654321u, 4u) == 0x87654321u);
    assert(init_read32(0x805eb8u) == 0x87654321u && init_read8(0x805ebcu) == 4u);
    assert(opencfw_em9305_callback_31d438() == 0x808000u);
    assert(opencfw_em9305_callback_320084() == 0x8032a0u);
    *(volatile uint8_t *)0x805b18u = 0x5au;
    assert(opencfw_em9305_callback_32056c(0x55331177u) == 0x5au);
    assert(calls_303d18 == 1u && calls_302ec8 == 1u);
    assert(opencfw_em9305_callback_31e604(0x01020304u) == 0x00010001u);
    assert(calls_303008 == 1u && calls_302ff4 == 1u && calls_30e42c == 1u);
    init_write32(0x3357acu, 0u);
    assert(opencfw_em9305_init_child_307980() == 0x8032a0u);
    assert(init_read8(0x802d30u) == 0u && init_read8(0x8032b0u) == 2u);
    init_write32(0x3357b0u, 0u);
    assert(opencfw_em9305_init_child_307980() == 0x802d20u);
    init_write32(0x3357a8u, 0u);
    assert(opencfw_em9305_init_child_307980() == 0x802a54u);
    puts("PASS 256 version states across five full lower bodies and four children");
    return 0;
}
