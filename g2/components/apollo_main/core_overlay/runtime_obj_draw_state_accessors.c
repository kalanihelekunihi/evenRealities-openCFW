/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room recovery of LVGL's `lv_obj_get_ext_draw_size` and
 * `lv_obj_get_layer_type` accessors at 0x00452DC8 and 0x00452DD8 in G2
 * firmware 2.2.6.10. Offsets follow the stock G2 `lv_obj_t` and spec_attr
 * layout recovered from adjacent object draw code.
 */

#if defined(OPEN_CFW_AM020_EXT_DRAW_SIZE_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_ext_draw_size(const void *obj)
{
    const unsigned char *bytes = (const unsigned char *)obj;
    const unsigned char *spec = *(const unsigned char * const *)(bytes + 8);
    if (spec == 0) {
        return 0;
    }
    unsigned int result = *(const unsigned int *)(spec + 0x2c);
    __asm__ volatile(
        ".rept 1\n"
        "nop\n"
        ".endr\n"
    );
    return result;
}
#endif

#if defined(OPEN_CFW_AM020_LAYER_TYPE_ONLY)
__attribute__((used, noinline))
unsigned int open_cfw_runtime_obj_get_layer_type(const void *obj)
{
    const unsigned char *bytes = (const unsigned char *)obj;
    const unsigned char *spec = *(const unsigned char * const *)(bytes + 8);
    if (spec == 0) {
        return 0;
    }
    unsigned int result = (*(const unsigned short *)(spec + 0x32) >> 10) & 3U;
    __asm__ volatile(
        ".rept 3\n"
        "nop\n"
        ".endr\n"
    );
    return result;
}
#endif
