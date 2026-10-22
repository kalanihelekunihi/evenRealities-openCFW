/* Production-test microphone capture, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\production_mic_func.c.
 * Native 0x58f4e4..0x58f865; literal pool 0x58f868..0x58f8cb.
 *
 * Both paths register a PCM handler for application id 0x10b with the audio
 * service: mode 0 is the codec microphone path, mode 1 the PDM path. With
 * the LC3 flag set (RAM 0x20004551) PCM is LC3-encoded before being handed
 * to the recorder; otherwise raw PCM is forwarded. Stereo capture encodes
 * the same frame with both codec-channel encoders (RAM 0x20106a7c and
 * 0x201074c0) and concatenates the two outputs. */
#include <stdint.h>
#include <stdbool.h>

#define PRODUCTION_APP_ID 0x10bu
#define PCM_SCRATCH_BYTES 400u

enum { PCM_SOURCE_CODEC = 0u, PCM_SOURCE_PDM = 1u };

extern volatile uint8_t g2_production_lc3_enable;   /* RAM 0x20004551 */
extern uint8_t g2_lc3_encoder_codec_left[];         /* RAM 0x20106a7c */
extern uint8_t g2_lc3_encoder_codec_right[];        /* RAM 0x201074c0 */
extern uint8_t g2_lc3_encoder_pdm[];                /* RAM 0x20107f04 */
extern volatile uint32_t g2_production_codec_mic_state; /* RAM 0x20074890 */

extern int32_t SVC_Lc3EncodeMono(const void *pcm, uint32_t pcm_bytes, void *out, uint32_t *out_bytes, void *encoder);
extern int32_t SVC_PcmRecoderProcess(uint8_t source, const void *data, uint32_t bytes);
extern void service_audio_recording_start(uint32_t source);
extern void service_audio_recording_stop(uint32_t source);
extern int32_t audio_register(uint32_t app_id, uint32_t mode, uint32_t callback);  /* SVC_PcmAppRegister 0x57ab78 */
extern int32_t audio_unregister(uint32_t app_id, uint32_t index);                  /* SVC_PcmAppUnregister 0x57acd0 */
extern void audio_app_stream_enable_53ca10(uint32_t enabled);  /* aud_send_message_type0 */
extern void audio_app_codec_enable_53ca32(uint32_t enabled);   /* aud_send_message_type1 */
extern void audio_app_first_hardware_prepare_57a926(void *encoder); /* service_audio_lc3_encoder_setup */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* 0x439be4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "prod.pcm"; /* ROM 0x78b7d4 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\production_mic_func.c"; /* ROM 0x6eee18 */
static const char cb_fmt[] = "Production test PCM callback: source=%d, size=%d"; /* ROM 0x72be94 */
static const char cb_fmt_short[] = "[prod.pcm]Production test PCM callback: source=%d, size=%d"; /* ROM 0x717a64 */
static const char fn_stereo[] = "production_pcm_callback_stereo"; /* ROM 0x7639d0 */
static const char fn_single[] = "production_pcm_callback_single"; /* ROM 0x7639f0 */
static const char fn_codec_init[] = "production_codec_mic_func_init"; /* ROM 0x763a10 */
static const char codec_single[] = "join in production_codec_mic_func_init and register production_pcm_callback_single"; /* ROM 0x6e9310 */
static const char codec_single_short[] = "[prod.pcm]join in production_codec_mic_func_init and register production_pcm_callback_single"; /* ROM 0x6de314 */
static const char codec_stereo[] = "join in production_codec_mic_func_init and register production_pcm_callback_stereo"; /* ROM 0x6e9364 */
static const char codec_stereo_short[] = "[prod.pcm]join in production_codec_mic_func_init and register production_pcm_callback_stereo"; /* ROM 0x6de374 */
static const char fn_codec_deinit[] = "production_codec_mic_func_deinit"; /* ROM 0x758118 */
static const char unregistered[] = "Production test PCM handler unregistered"; /* ROM 0x7418bc */
static const char unregistered_short[] = "[prod.pcm]Production test PCM handler unregistered"; /* ROM 0x72bec8 */
static const char fn_pdm_init[] = "production_pdm_mic_func_init"; /* ROM 0x763a30 */
static const char pdm_join[] = "join in production_pdm_mic_func_init"; /* ROM 0x74c8dc */
static const char pdm_join_short[] = "[prod.pcm]join in production_pdm_mic_func_init"; /* ROM 0x736bb4 */
static const char fn_pdm_deinit[] = "production_pdm_mic_func_deinit"; /* ROM 0x763a50 */

static bool log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static bool log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

static void log_callback(const char *fn, uint32_t line, uint8_t source, uint32_t size)
{
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn, line, cb_fmt, source, size);
    if (log_compressed_on())
        (void)compress_log_output(0x10800000u, cb_fmt_short, cb_fmt_short, source, size);
}

/* Only codec PCM (source 0) is handled; other sources are dropped. */
void production_pcm_callback_stereo(uint8_t source, const void *pcm, uint32_t size)
{
    uint8_t encoded[PCM_SCRATCH_BYTES];
    uint8_t joined[PCM_SCRATCH_BYTES];
    uint32_t encoded_bytes;

    log_callback(fn_stereo, 0x15u, source, size);
    (void)aeabi_memset_43c0e4(encoded, PCM_SCRATCH_BYTES, 0);
    (void)aeabi_memset_43c0e4(joined, PCM_SCRATCH_BYTES, 0);
    encoded_bytes = 0u;
    if (source != PCM_SOURCE_CODEC)
        return;
    if (g2_production_lc3_enable == 0u) {
        (void)SVC_PcmRecoderProcess(source, pcm, size);
        return;
    }
    (void)SVC_Lc3EncodeMono(pcm, size, encoded, &encoded_bytes, g2_lc3_encoder_codec_left);
    (void)audio_queue_copy_bytes(joined, encoded, encoded_bytes);
    (void)SVC_Lc3EncodeMono(pcm, size, encoded, &encoded_bytes, g2_lc3_encoder_codec_right);
    (void)audio_queue_copy_bytes(joined + encoded_bytes, encoded, encoded_bytes);
    (void)SVC_PcmRecoderProcess(source, joined, encoded_bytes * 2u);
}

void production_pcm_callback_single(uint8_t source, const void *pcm, uint32_t size)
{
    uint8_t encoded[PCM_SCRATCH_BYTES];
    uint32_t encoded_bytes;

    log_callback(fn_single, 0x4bu, source, size);
    (void)aeabi_memset_43c0e4(encoded, PCM_SCRATCH_BYTES, 0);
    encoded_bytes = 0u;
    if (g2_production_lc3_enable == 0u) {
        (void)SVC_PcmRecoderProcess(source, pcm, size);
        return;
    }
    if (source == PCM_SOURCE_CODEC)
        (void)SVC_Lc3EncodeMono(pcm, size, encoded, &encoded_bytes, g2_lc3_encoder_codec_right);
    else if (source == PCM_SOURCE_PDM)
        (void)SVC_Lc3EncodeMono(pcm, size, encoded, &encoded_bytes, g2_lc3_encoder_pdm);
    (void)SVC_PcmRecoderProcess(source, encoded, encoded_bytes);
}

/* channels: 0 registers the single-channel handler, 1 the stereo handler. */
int32_t production_codec_mic_func_init(uint8_t channels)
{
    g2_production_codec_mic_state = 0u;
    if (channels == 0u) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_codec_init, 0x6du, codec_single);
        if (log_compressed_on())
            (void)compress_log_output(0x10000000u, codec_single_short, codec_single_short);
        (void)audio_register(PRODUCTION_APP_ID, PCM_SOURCE_CODEC, (uint32_t)(uintptr_t)&production_pcm_callback_single);
    } else if (channels == 1u) {
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_codec_init, 0x72u, codec_stereo);
        if (log_compressed_on())
            (void)compress_log_output(0x10000000u, codec_stereo_short, codec_stereo_short);
        (void)audio_register(PRODUCTION_APP_ID, PCM_SOURCE_CODEC, (uint32_t)(uintptr_t)&production_pcm_callback_stereo);
    }
    audio_app_stream_enable_53ca10(1u);
    service_audio_recording_start(PCM_SOURCE_CODEC);
    return 0;
}

int32_t production_codec_mic_func_deinit(void)
{
    audio_app_stream_enable_53ca10(0u);
    int32_t status = audio_unregister(PRODUCTION_APP_ID, PCM_SOURCE_CODEC);
    if (status == 0) {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_codec_deinit, 0x82u, unregistered);
        if (log_compressed_on())
            (void)compress_log_output(0x0c000000u, unregistered_short, unregistered_short);
        service_audio_recording_stop(PCM_SOURCE_CODEC);
        audio_app_first_hardware_prepare_57a926(g2_lc3_encoder_codec_left);
        audio_app_first_hardware_prepare_57a926(g2_lc3_encoder_codec_right);
    }
    return status;
}

int32_t production_pdm_mic_func_init(void)
{
    if (log_extended_on())
        audio_log_extended(4u, module_tag, source_file, fn_pdm_init, 0x92u, pdm_join);
    if (log_compressed_on())
        (void)compress_log_output(0x10000000u, pdm_join_short, pdm_join_short);
    (void)audio_register(PRODUCTION_APP_ID, PCM_SOURCE_PDM, (uint32_t)(uintptr_t)&production_pcm_callback_single);
    audio_app_codec_enable_53ca32(1u);
    service_audio_recording_start(PCM_SOURCE_PDM);
    return 0;
}

int32_t production_pdm_mic_func_deinit(void)
{
    audio_app_codec_enable_53ca32(0u);
    int32_t status = audio_unregister(PRODUCTION_APP_ID, PCM_SOURCE_PDM);
    if (status == 0) {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_pdm_deinit, 0xa0u, unregistered);
        if (log_compressed_on())
            (void)compress_log_output(0x0c000000u, unregistered_short, unregistered_short);
        service_audio_recording_stop(PCM_SOURCE_PDM);
        audio_app_first_hardware_prepare_57a926(g2_lc3_encoder_pdm);
    }
    return status;
}
