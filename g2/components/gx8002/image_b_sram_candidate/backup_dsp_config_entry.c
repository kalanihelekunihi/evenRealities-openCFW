/* Image-B native 0x1000de94..0x1000de9d and 0x1000deb4..0x1000dec9.
 * The first is a three-register call-through which returns zero; the
 * second copies exactly four words into product RAM at 0x2002d7a4.
 * Stock SHA256 d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_dsp_transform_1000d2a4(
    const void *context, void *samples, uint32_t phase);
extern volatile uint32_t gx8002_image_b_dsp_config_2002d7a4[4];

uint32_t gx8002_image_b_dsp_transform_entry_1000de94(
    const void *context, void *samples, uint32_t phase)
{
    (void)gx8002_image_b_dsp_transform_1000d2a4(context, samples, phase);
    return 0u;
}

uint32_t gx8002_image_b_dsp_config_copy_1000deb4(const uint32_t *source)
{
    for (uint32_t i = 0u; i < 4u; ++i) {
        gx8002_image_b_dsp_config_2002d7a4[i] = source[i];
    }
    return 0u;
}
