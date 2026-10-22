/* Byte-wise strcmp at native 0x46cacc..0x46cade (between the uLED preprocess and the
 * LVGL font manager; called as strcmp by the font, KVDB, NVDB, EFS, logger-setting and
 * shell code). Bytes compare unsigned; the result is the difference of the first
 * mismatching bytes, or 0. */
#include <stdint.h>

int32_t string_compare_46cacc(const char *a, const char *b)
{
    const uint8_t *p = (const uint8_t *)a;
    const uint8_t *q = (const uint8_t *)b;
    uint32_t ca;
    uint32_t cb;
    do {
        ca = *p++;
        cb = *q++;
    } while (ca != 0u && ca == cb);
    return (int32_t)(ca - cb);
}
