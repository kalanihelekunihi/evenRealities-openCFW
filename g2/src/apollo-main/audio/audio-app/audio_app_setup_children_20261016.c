/* First-app setup descendants at 0x53ca10, 0x53ca32 and 0x57a926. */
#include <stdint.h>

extern void audio_app_control_packet_53c638(const void *);
extern void *lc3_setup_encoder(int dt_us, int sr_hz, int sr_pcm_hz, void *mem); /* liblc3 0x591374 */

/* Stock context begins at 0x20108948; observed direct access ends at +0x1f. */
uint8_t g2_audio_first_hardware_context_20108948[0x20];

void audio_app_stream_enable_53ca10(uint32_t enabled) {
    uint32_t packet[3] = {0u, 1u, (uint8_t)enabled};
    audio_app_control_packet_53c638(packet);
}

void audio_app_codec_enable_53ca32(uint32_t enabled) {
    uint32_t packet[3] = {1u, 1u, (uint8_t)enabled};
    audio_app_control_packet_53c638(packet);
}

void audio_app_first_hardware_prepare_57a926(void *context) {
    if (!context)
        return;
    uint8_t *bytes = (uint8_t *)context;
    uint32_t first = *(uint32_t *)(bytes + 4u);
    uint32_t second = *(uint32_t *)(bytes + 8u);
    void *handle = lc3_setup_encoder((int)first, (int)second, 0, bytes + 0x1cu);
    *(uint32_t *)(bytes + 0x18u) = (uint32_t)(uintptr_t)handle;
}
