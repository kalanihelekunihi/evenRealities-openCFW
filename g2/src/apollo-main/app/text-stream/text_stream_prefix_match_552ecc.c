/* Stock text-stream common-prefix count, 0x552ecc. */
#include <stdint.h>
#include <stddef.h>

extern size_t strlen(const char *);

uint32_t audio_text_stream_prefix_match_552ecc(const char *left, const char *right) {
    if (!left || !right)
        return 0;
    uint32_t limit = (uint32_t)strlen(left);
    uint32_t right_length = (uint32_t)strlen(right);
    if ((int32_t)limit >= (int32_t)right_length)
        limit = right_length;
    uint32_t index = 0;
    while ((int32_t)index < (int32_t)limit) {
        if ((uint8_t)left[index] != (uint8_t)right[index])
            break;
        ++index;
    }
    return index;
}
