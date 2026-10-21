/* Loaded image-B typed initialization, stock normal-copy mapping.
 * Source SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 * The gsensor state at IRAM 0x10016f60 / runtime 0x20016f60 is one word,
 * read twice by native 0x100089e8. The 21 IMCRA IEEE binary32 words at
 * IRAM 0x10016fb8..0x1001700b / runtime 0x20016fb8..0x2001700b are
 * consumed by native 0x1000e784. Their exact 84-byte SHA256 is
 * f99f330ad9cfd2d7a23ce8b9841877ef452c6515387b2a2f38eaf4813f48889d.
 * These are named product settings, not an opaque copied payload.
 */
#include <stdint.h>

volatile uint32_t gx8002_image_b_gsensor_workstate_20016f60 = 1u;

volatile uint32_t gx8002_image_b_imcra_cfg_words_20016fb8[21] = {
    /* B state parameters at 0x20016fb8..0x20016fcc. */
    UINT32_C(0x3d4ccccd), UINT32_C(0x40a00000), UINT32_C(0x41700000),
    UINT32_C(0x41a00000), UINT32_C(0x3e4ccccd), UINT32_C(0xc2120000),
    /* C state parameters at 0x20016fd0..0x20016fe4. */
    UINT32_C(0x3c23d70a), UINT32_C(0x3c23d70a), UINT32_C(0x40a00000),
    UINT32_C(0x42200000), UINT32_C(0x3ca3d70a), UINT32_C(0xc2200000),
    /* A state parameters at 0x20016fe8..0x20016ff4. */
    UINT32_C(0x3ba3d70a), UINT32_C(0x40a00000), UINT32_C(0x3dcccccd),
    UINT32_C(0xc1700000),
    /* D state and finish parameters at 0x20016ff8..0x20017008. */
    UINT32_C(0x3c23d70a), UINT32_C(0xc1200000), UINT32_C(0x3ba3d70a),
    UINT32_C(0x3ca3d70a), UINT32_C(0xc2480000),
};

/* Native CRT clears 0x20017090..0x2002d79c on its cold path. The retained
 * path skips that clear, preserving the prior SRAM value. */
__attribute__((section(".bss.image_b_token_cursor")))
char *gx8002_image_b_token_cursor_2002d3e0;

/* Read/write dispatchers use this shadow at 0x20017398. It lies within the
 * conditional native CRT BSS clear interval. */
__attribute__((section(".bss.image_b_platform_shadow")))
volatile uint32_t gx8002_image_b_platform_shadow_20017398;
