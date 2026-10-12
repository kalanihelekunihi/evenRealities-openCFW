/* SPDX-License-Identifier: MIT
 * Image-B record callback 0x10015bc8..0x10015cf0, reconstructed from the
 * native C-SKY control flow. The five-word 0x2002d75c state is initialized
 * by 0x1000a418; the function pointer at the heap-end word is external data.
 */
#include <stdint.h>

extern uint32_t gx8002_image_b_audio_state_address_10009e48(void);
extern uint32_t gx8002_image_b_audio_word_28_10009f74(void);
extern uint32_t gx8002_image_b_audio_word_24_10009f50(void);
extern uint32_t gx8002_image_b_audio_word_3c_10009f90(void);
extern uint32_t gx8002_image_b_audio_one_10009f8c(void);

typedef int32_t (*record_sink)(uint32_t, uint32_t *);
#define RECORD_STATE ((volatile uint32_t *)(uintptr_t)UINT32_C(0x2002d75c))
#define RECORD_SINK (*(volatile record_sink *)(uintptr_t)UINT32_C(0x2002cb80))

int32_t gx8002_image_b_audio_record_10015bc8(uint32_t channel,
                                                uint32_t *sdc_address)
{
    if ((channel & 1u) != 0u) {
        uint32_t state = gx8002_image_b_audio_state_address_10009e48();
        uint32_t frame = *(volatile uint32_t *)(uintptr_t)(state + 0x24u) << 9;
        uint32_t last = sdc_address[0] / frame;
        uint32_t capacity = (uint32_t)(
            (int32_t)gx8002_image_b_audio_word_28_10009f74() /
            (int32_t)gx8002_image_b_audio_word_24_10009f50());
        if ((RECORD_STATE[4] & 0xf0u) != 0u) {
            RECORD_STATE[1] = last + 2u;
            RECORD_STATE[0] = last + 2u;
            RECORD_STATE[2] = last;
            RECORD_STATE[4] = (RECORD_STATE[4] & ~UINT32_C(0xff)) | 1u;
        }
        uint32_t cursor = RECORD_STATE[1];
        if (last == cursor % capacity) return 0;
        do {
            if (gx8002_image_b_audio_word_3c_10009f90() < cursor) {
                uint32_t distance = cursor - RECORD_STATE[0];
            if (distance >= gx8002_image_b_audio_word_3c_10009f90() -
                                gx8002_image_b_audio_one_10009f8c())
                    return 0;
            }
            (void)RECORD_SINK(cursor, sdc_address);
            cursor = RECORD_STATE[1] + 1u;
            RECORD_STATE[1] = cursor;
        } while (last != cursor % capacity);
        return 0;
    }
    if ((channel & 2u) == 0u) return 0;
    uint32_t state = gx8002_image_b_audio_state_address_10009e48();
    uint32_t frame = *(volatile uint32_t *)(uintptr_t)(state + 0x24u) << 9;
    uint32_t last = sdc_address[1] / frame;
    uint32_t capacity = (uint32_t)(
        (int32_t)gx8002_image_b_audio_word_28_10009f74() /
        (int32_t)gx8002_image_b_audio_word_24_10009f50());
    if ((RECORD_STATE[4] & 0xf0u) != 0u) {
        uint32_t flags = (RECORD_STATE[4] & ~UINT32_C(0xff)) | 1u;
        RECORD_STATE[1] = last + 2u;
        RECORD_STATE[0] = last + 2u;
        RECORD_STATE[2] = last;
        RECORD_STATE[4] = flags;
    }
    uint32_t cursor = RECORD_STATE[1];
    if (last == cursor % capacity) return 0;
    do {
        if (capacity < cursor) {
            uint32_t distance = cursor - RECORD_STATE[0];
            if (distance >= capacity - 1u) return 0;
        }
        (void)RECORD_SINK(cursor, sdc_address + 1);
        cursor = RECORD_STATE[1] + 1u;
        RECORD_STATE[1] = cursor;
    } while (last != cursor % capacity);
    return 0;
}
