/* SPDX-License-Identifier: MIT
 * Stock BINH-B stage-1 loader at 0x10000d4c..0x10000dd0.
 * Original stage1 SHA256 a80924ccf78205ef1761c4f568d4ce31f909635bf3ad7eecfaed250ad801626c.
 * This describes both native marker branches. It is a separate stage-1 C
 * candidate and does not extend the stock normal payload transfer.
 */
#include <stdint.h>
#include <spl/spl.h>
extern volatile struct boot_info gx8002_stage1_boot_info;
extern void gx8002_image_b_stage1_reset_10000100(void);
extern void gx8002_image_b_stage2_reset_10003100(void);

extern uint32_t gx8002_image_b_stage1_flash_read_10000fdc(
    uint32_t source_offset, void *destination, uint32_t bytes);

int32_t gx8002_image_b_stage1_loader_10000d4c(void)
{
    volatile uint32_t *const package_offset =
        &gx8002_stage1_boot_info.info.value;
    volatile uint32_t *const marker =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x20033ffc);
    volatile uint32_t *const entry_word =
        (volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d3e4);
    uint32_t word;
    uint32_t package = *package_offset;
    uint32_t stage2_package = package + UINT32_C(0x3000);

    if (*marker != UINT32_C(0xaabbccdd)) {
        (void)gx8002_image_b_stage1_flash_read_10000fdc(
            stage2_package, &word, 4u);
        (void)gx8002_image_b_stage1_flash_read_10000fdc(
            stage2_package + word + 4u,
            (void *)(uintptr_t)UINT32_C(0x10003000), UINT32_C(0x1408c));
        *entry_word = (uint32_t)(uintptr_t)&gx8002_image_b_stage2_reset_10003100;
        gx8002_image_b_stage2_reset_10003100();
    } else {
        /* Native code reads a word from package+0x323b0, then makes a
         * zero-byte reader call at that word+0x323b4 before reset. The
         * zero-byte call is retained because its reader-side effects have
         * not been ruled out. */
        (void)gx8002_image_b_stage1_flash_read_10000fdc(
            package + UINT32_C(0x323b0), &word, 4u);
        (void)gx8002_image_b_stage1_flash_read_10000fdc(
            word + UINT32_C(0x323b4),
            (void *)(uintptr_t)UINT32_C(0x20000000), 0u);
        *entry_word = (uint32_t)(uintptr_t)&gx8002_image_b_stage1_reset_10000100;
        gx8002_image_b_stage1_reset_10000100();
    }
    return 0;
}
