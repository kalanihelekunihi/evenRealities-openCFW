/* Native normal-copy 0x10016f64..0x10016f73 -> 0x20016f64..0x20016f73.
 * The first pair is indexed by UART RX channel at 0x1000b1d8. The audio
 * callback 0x1000bef4 reads the one-shot flag at 0x20016f6c and increments
 * the signed count at 0x20016f70 until 1000. The four initial values below
 * are the authenticated initialized state, not inferred runtime defaults.
 * This file is an unselected placement candidate while the image-B graph
 * snapshot is held for the combined Codec build. */
#include <stddef.h>
#include <stdint.h>

typedef struct {
    uint32_t uart_rx_header_progress[2];
    uint32_t audio_first_callback_pending;
    int32_t audio_callback_count;
} image_b_audio_runtime_initialized_state;

_Static_assert(sizeof(image_b_audio_runtime_initialized_state) == 16,
               "native initialized state extent");
_Static_assert(offsetof(image_b_audio_runtime_initialized_state,
                        audio_first_callback_pending) == 8,
               "native one-shot flag offset");

volatile image_b_audio_runtime_initialized_state
gx8002_image_b_audio_runtime_state_20016f64
    __attribute__((section(".data.image_b.audio_runtime_state"), used)) = {
        .uart_rx_header_progress = {4u, 4u},
        .audio_first_callback_pending = 1u,
        .audio_callback_count = -4,
    };
