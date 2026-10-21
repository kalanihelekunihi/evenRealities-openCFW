/* Image-B native 0x10008a04..0x10008a9d, formatter field emitter.
 * The callback receives byte, context, output index and caller state in
 * r0-r3. Digit storage is consumed in reverse order as in the native loop.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

typedef uint32_t (*gx_image_b_emit_callback)(
    uint32_t byte, uint32_t context, uint32_t index, uint32_t state);

uint32_t gx8002_image_b_format_emit_10008a04(
    gx_image_b_emit_callback emit, uint32_t context, uint32_t index,
    uint32_t state, const uint8_t *reversed, uint32_t count,
    uint32_t width, uint32_t flags)
{
    uint32_t emitted = 0u;
    if ((flags & 3u) == 0u && count < width) {
        for (uint32_t i = count; i < width; ++i) {
            (void)emit(0x20u, context, index++, state);
            ++emitted;
        }
    }
    for (uint32_t i = count; i != 0u; --i) {
        (void)emit(reversed[i - 1u], context, index++, state);
        ++emitted;
    }
    if ((flags & 2u) != 0u) {
        for (; emitted < width; ++emitted) {
            (void)emit(0x20u, context, index++, state);
        }
    }
    return index;
}
