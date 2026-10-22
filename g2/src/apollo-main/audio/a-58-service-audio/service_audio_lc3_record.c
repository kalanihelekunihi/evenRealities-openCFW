/* Audio service: LC3 mono encode, PCM consumer dispatch and PCM recording to
 * LittleFS, stock D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_audio.c
 * (module tag "svc.audio" ROM 0x78be1c, path ROM 0x7053c4).
 * Native 0x57a900..0x57a925, 0x57a940..0x57ab77, 0x57adf8..0x57af8b and
 * 0x57af8c..0x57b351, 0x57b352..0x57b377; literal pool 0x57b37c..0x57b443.
 * Elsewhere in g2/src: SVC_PcmAppRegister 0x57ab78 (audio/pcm-register,
 * audio_register), SVC_PcmAppUnregister 0x57acd0 (audio/pcm-unregister,
 * audio_unregister), the LC3 encoder setup 0x57a926
 * (audio_app_first_hardware_prepare_57a926) and service_audio_recording_stop
 * 0x57b312 (system/log/diagnostic-deinit, audio_recording_stop_selected).
 *
 * The LC3 codec is Google liblc3 (third-party/upstream/liblc3); the four
 * calls used here are lc3_frame_samples 0x590e64, lc3_frame_bytes 0x590f78,
 * lc3_setup_encoder 0x591374 and lc3_encode 0x59138a, and the encoder record
 * format byte is enum lc3_pcm_format (S16, S24, S24_3LE, FLOAT).
 *
 * PCM source 0 (codec, the two-microphone front end) without a registered
 * consumer is turned into one 205-byte BLE streaming packet per frame:
 * LC3 bytes, SSR ratio (u16), TDOA angle (s16), and a sequence byte at +204.
 * Recording rows (one per source) write <prefix><basename>_<NN>.pcm under
 * /audio/, rotating files at 1 MiB. */
#include <stdint.h>
#include <stddef.h>

#define SA_SOURCE_COUNT       2u
#define SA_PACKET_LEN         0xcdu   /* 205-byte BLE streaming packet */
#define SA_PACKET_SEQ         0xccu   /* sequence byte offset */
#define SA_LOG_EVERY          40      /* packets between statistics logs */
#define SA_MIN_FRAME_BYTES    20
#define SA_RECORD_FILE_LIMIT  0x100000u /* rotate when the file would exceed 1 MiB */
#define SA_RECORD_FILE_MAX    1u      /* stock wraps the file index at 1 */
#define SA_PATH_LEN           0x20u
#define SA_LFS_ERR_NOENT      (-2)
#define SA_LFS_INFO_SIZE      0x108u  /* struct lfs_info, LFS_NAME_MAX 255 */

/* LC3 encoder record (g2_lc3_encoder_codec_left/right/pdm, 0x20108948). */
typedef struct {
    uint8_t pcm_format;   /* +0x00 enum lc3_pcm_format */
    int32_t dt_us;        /* +0x04 frame duration */
    int32_t sr_hz;        /* +0x08 sample rate */
    int32_t channels;     /* +0x0c interleaved channels in the PCM buffer */
    int32_t channel;      /* +0x10 channel encoded when channels > 1 */
    int32_t bitrate;      /* +0x14 */
    void *encoder;        /* +0x18 lc3_encoder_t, set up on first use */
    uint8_t mem[];        /* +0x1c lc3 encoder memory */
} sa_lc3_encoder_t;
_Static_assert(offsetof(sa_lc3_encoder_t, encoder) == 0x18u, "lc3 encoder handle");
_Static_assert(offsetof(sa_lc3_encoder_t, mem) == 0x1cu, "lc3 encoder memory");

/* PCM consumer row at 0x20073c20 + 12 * source (see audio/pcm-registration). */
typedef struct {
    uint32_t owner;       /* +0 app ID */
    uint8_t source;       /* +4 */
    uint8_t reserved[3];
    void (*callback)(uint8_t source, const uint8_t *buffer, uint32_t length); /* +8 */
} sa_pcm_registration_t;
_Static_assert(sizeof(sa_pcm_registration_t) == 12u, "registration row is 12 bytes");

/* Recording row at 0x20073c08 + 12 * source. */
typedef struct {
    void *file;           /* +0x0 */
    uint32_t written;     /* +0x4 bytes in the current file */
    uint16_t index;       /* +0x8 file number in the name */
    uint8_t started;      /* +0xa */
    uint8_t first;        /* +0xb next open reuses the current index */
} sa_recording_t;
_Static_assert(sizeof(sa_recording_t) == 12u, "recording row is 12 bytes");

extern uint32_t g2_pcm_registration_rows[];                       /* RAM 0x20073c20, 2 rows */
extern sa_recording_t g2_audio_recording_rows_20073c08[SA_SOURCE_COUNT]; /* RAM 0x20073c08 */
extern const char *g2_audio_recording_basenames_200036d0[SA_SOURCE_COUNT]; /* RAM 0x200036d0 (.data) */
extern uint8_t g2_audio_first_hardware_context_20108948[];         /* RAM 0x20108948 LC3 encoder record */
extern volatile uint8_t g2_audio_lc3_packet_seq_2007500e;          /* RAM 0x2007500e */
extern uint8_t audio_file_lfs_context[];                           /* RAM 0x20071ac8 lfs_t */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern void elog_hexdump_43dacc(const char *name, uint32_t width, const uint8_t *buf, uint32_t size);
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */
extern uint32_t osKernelGetTickCount(void);                                   /* 0x4490cc */
extern void *file_open(const char *path, const char *mode);                   /* 0x474550 */
extern int32_t file_close(void *file);                                        /* 0x4745f4 */
extern uint32_t file_write(const void *buf, uint32_t size, uint32_t count, void *file); /* 0x474682 */
extern int32_t lfs_stat_4cfa8a(void *lfs, const char *path, void *info);
extern int32_t audio_file_lfs_mkdir_4cfc5c(void *lfs, const char *path);
extern uint32_t Thread_MsgStreamingNotifyByBle(const void *payload, uint16_t length); /* 0x475d78 */
extern int32_t service_algo_process(const int16_t *pcm, uint32_t bytes, uint16_t *ratio, int16_t *angle); /* 0x591bfc */
extern void service_algo_front_buffer_get(int16_t **buffer, uint32_t *bytes); /* 0x5915dc */
extern int32_t lc3_frame_samples(int32_t dt_us, int32_t sr_hz);   /* liblc3 0x590e64 */
extern int32_t lc3_frame_bytes(int32_t dt_us, int32_t bitrate);    /* liblc3 0x590f78 */
extern void *lc3_setup_encoder(int32_t dt_us, int32_t sr_hz, int32_t sr_pcm_hz, void *mem); /* liblc3 0x591374 */
extern int32_t lc3_encode(void *encoder, uint32_t fmt, /* liblc3 0x59138a; fmt is a one-byte enum */ const void *pcm, int32_t stride,
                                 int32_t nbytes, void *out);

const char *service_audio_recording_basename_get(uint8_t source);
void service_audio_format_recording_path(uint8_t source, uint16_t index, char *dst, uint32_t size);
uint32_t service_audio_pcm_sample_bytes(uint8_t format);
int32_t SVC_Lc3EncodeMono(const void *pcm, uint32_t pcm_bytes, void *out, uint32_t *out_bytes, void *encoder);
int32_t service_audio_recording_open_next(uint8_t source);
void service_audio_recording_directory_prepare(void);
void service_audio_recording_start(uint8_t source);

static const char module_tag[] = "svc.audio"; /* ROM 0x78be1c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio.c"; /* ROM 0x7053c4 */
static const char audio_dir[] = "/audio/"; /* ROM 0x78e4ec */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Compressed-log word: level in bits 26+, argument count in bits 22+. */
#define SA_CLOG(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define SA_LOG0(level, fn, line, fmt, cfmt) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt)); \
        if (log_compressed_on()) (void)compress_log_output(SA_CLOG((level), 0), (cfmt), (cfmt)); \
    } while (0)
#define SA_LOGN(level, nargs, fn, line, fmt, cfmt, ...) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), __VA_ARGS__); \
        if (log_compressed_on()) (void)compress_log_output(SA_CLOG((level), (nargs)), (cfmt), (cfmt), __VA_ARGS__); \
    } while (0)

/* Bytes per sample for enum lc3_pcm_format; 0 = unknown format. */
uint32_t service_audio_pcm_sample_bytes(uint8_t format)
{
    if (format == 0u)
        return 2u;      /* LC3_PCM_FORMAT_S16 */
    if (format == 2u)
        return 3u;      /* LC3_PCM_FORMAT_S24_3LE */
    if (format < 2u)
        return 4u;      /* LC3_PCM_FORMAT_S24 */
    if (format == 3u)
        return 4u;      /* LC3_PCM_FORMAT_FLOAT */
    return 0u;
}

/* Encode whole LC3 frames of one channel; pcm_bytes must be a multiple of
 * the interleaved frame size. Returns 0 or -1. */
int32_t SVC_Lc3EncodeMono(const void *pcm, uint32_t pcm_bytes, void *out, uint32_t *out_bytes, void *encoder)
{
    static const char fn[] = "SVC_Lc3EncodeMono"; /* ROM 0x782e20 */
    static const char null_param[] = "NULL parameter: buf_pcm=%p, buf_output=%p, output_bytes=%p, parms=%p"; /* ROM 0x6fcb24 */
    static const char null_param_c[] = "[svc.audio]NULL parameter: buf_pcm=%p, buf_output=%p, output_bytes=%p, parms=%p"; /* ROM 0x6ef6d8 */
    static const char bad_frame[] = "Invalid frame parameters: frame_samples=%d, nbytes=%d"; /* ROM 0x7225f0 */
    static const char bad_frame_c[] = "[svc.audio]Invalid frame parameters: frame_samples=%d, nbytes=%d"; /* ROM 0x705408 */
    static const char bad_format[] = "Invalid PCM format: %d"; /* ROM 0x77b2fc */
    static const char bad_format_c[] = "[svc.audio]Invalid PCM format: %d"; /* ROM 0x75918c */
    static const char enc_fail[] = "lc3_encode failed at frame %d, ret=%d"; /* ROM 0x74d804 */
    static const char enc_fail_c[] = "[svc.audio]lc3_encode failed at frame %d, ret=%d"; /* ROM 0x72ce38 */
    sa_lc3_encoder_t *parms = (sa_lc3_encoder_t *)encoder;

    if (pcm == NULL || out == NULL || out_bytes == NULL || parms == NULL) {
        SA_LOGN(1, 4, fn, 0x7cu, null_param, null_param_c, pcm, out, out_bytes, parms);
        return -1;
    }
    int32_t frame_samples = lc3_frame_samples(parms->dt_us, parms->sr_hz);
    int32_t nbytes = lc3_frame_bytes(parms->dt_us, parms->bitrate);
    if (frame_samples < 1 || nbytes < SA_MIN_FRAME_BYTES) {
        SA_LOGN(1, 2, fn, 0x84u, bad_frame, bad_frame_c, frame_samples, nbytes);
        return -1;
    }
    uint32_t sample_bytes = service_audio_pcm_sample_bytes(parms->pcm_format);
    if (sample_bytes == 0u) {
        SA_LOGN(1, 1, fn, 0x8bu, bad_format, bad_format_c, parms->pcm_format);
        return -1;
    }
    if (parms->encoder == NULL)
        parms->encoder = lc3_setup_encoder(parms->dt_us, parms->sr_hz, 0, parms->mem);

    uint32_t frame_bytes = sample_bytes * ((uint32_t)parms->channels * (uint32_t)frame_samples);
    if (pcm_bytes % frame_bytes != 0u)
        return -1;
    int32_t frames = (int32_t)(pcm_bytes / frame_bytes);
    const uint8_t *src = (const uint8_t *)pcm;
    uint8_t *dst = (uint8_t *)out;
    *out_bytes = 0u;
    for (int32_t frame = 0; frame < frames; frame++) {
        const uint8_t *channel_pcm;
        int32_t stride;
        if (parms->channels == 1) {
            channel_pcm = src;
            stride = 1;
        } else {
            channel_pcm = src + sample_bytes * (uint32_t)parms->channel;
            stride = parms->channels;
        }
        int32_t ret = lc3_encode(parms->encoder, parms->pcm_format, channel_pcm, stride, nbytes, dst);
        if (ret != 0) {
            SA_LOGN(1, 2, fn, 0xb0u, enc_fail, enc_fail_c, frame, ret);
            return -1;
        }
        src += frame_bytes;
        dst += nbytes;
        *out_bytes = (uint32_t)nbytes + *out_bytes;
    }
    return 0;
}

/* PCM frame sink for the codec (0) and PDM (1) threads: a registered
 * consumer for that source gets the raw frame; otherwise source 0 is run
 * through the front-end algorithm, LC3-encoded and streamed over BLE. */
void SVC_PcmAppProcessData(uint8_t source, const uint8_t *buffer, uint32_t length)
{
    static const char fn[] = "SVC_PcmAppProcessData"; /* ROM 0x77b344 */
    static const char stats[] = "[%d] pcm size=%d, lc3 size=%d, ssr=%d, tdoa=%d, total use time=%dms"; /* ROM 0x70544c */
    static const char stats_c[] = "[svc.audio][%d] pcm size=%d, lc3 size=%d, ssr=%d, tdoa=%d, total use time=%dms"; /* ROM 0x6ef728 */
    static const char dump_name[] = "lc3_data"; /* ROM 0x78be28 */
    const sa_pcm_registration_t *rows = (const sa_pcm_registration_t *)(void *)g2_pcm_registration_rows;

    if (source >= SA_SOURCE_COUNT || buffer == NULL || length == 0u)
        return;
    if (rows[source].callback != NULL && rows[source].source == source) {
        rows[source].callback(source, buffer, length);
        return;
    }
    if (source != 0u)
        return;

    uint8_t packet[SA_PACKET_LEN];
    (void)aeabi_memset_43c0e4(packet, SA_PACKET_LEN, 0);
    uint32_t lc3_bytes = 0u;
    uint16_t ssr = 0u;
    int16_t tdoa = 0;
    int16_t *front = NULL;
    uint32_t front_bytes = 0u;
    uint32_t start = osKernelGetTickCount();
    (void)service_algo_process((const int16_t *)(const void *)buffer, length, &ssr, &tdoa);
    service_algo_front_buffer_get(&front, &front_bytes);
    (void)SVC_Lc3EncodeMono(front, front_bytes, packet, &lc3_bytes, g2_audio_first_hardware_context_20108948);
    (void)audio_queue_copy_bytes(&packet[lc3_bytes], &ssr, 2u);
    (void)audio_queue_copy_bytes(&packet[lc3_bytes + 2u], &tdoa, 2u);
    packet[SA_PACKET_SEQ] = g2_audio_lc3_packet_seq_2007500e;
    g2_audio_lc3_packet_seq_2007500e = (uint8_t)(g2_audio_lc3_packet_seq_2007500e + 1u);
    if (((int32_t)g2_audio_lc3_packet_seq_2007500e - 1) % SA_LOG_EVERY == 0) {
        SA_LOGN(3, 6, fn, 0x112u, stats, stats_c, (int32_t)g2_audio_lc3_packet_seq_2007500e - 1, length,
                lc3_bytes, ssr, tdoa, osKernelGetTickCount() - start);
        elog_hexdump_43dacc(dump_name, 8u, packet, 8u);
    }
    (void)Thread_MsgStreamingNotifyByBle(packet, SA_PACKET_LEN);
}

/* "/audio/<basename>_<NN>.pcm" */
void service_audio_format_recording_path(uint8_t source, uint16_t index, char *dst, uint32_t size)
{
    static const char path_fmt[] = "%s%s_%02d%s"; /* ROM 0x78be34 */
    static const char suffix[] = ".pcm"; /* ROM 0x78e4f4 */
    const char *basename = service_audio_recording_basename_get(source);
    (void)g2_audio_dump_snprintf(dst, size, path_fmt, audio_dir, basename, index, suffix);
}

const char *service_audio_recording_basename_get(uint8_t source)
{
    return g2_audio_recording_basenames_200036d0[source];
}

/* Stock create_new_file: close the current file and open the next one ("wb").
 * Returns 0 or -1. */
int32_t service_audio_recording_open_next(uint8_t source)
{
    static const char fn[] = "create_new_file"; /* ROM 0x7886f0 */
    static const char write_mode[] = "wb"; /* inline literal-pool word 0x57b1f0 */
    static const char open_fail[] = "file open failed"; /* ROM 0x782e48 */
    static const char open_fail_c[] = "[svc.audio]file open failed"; /* ROM 0x770bf4 */
    sa_recording_t *rows = g2_audio_recording_rows_20073c08;
    char path[SA_PATH_LEN];

    if (rows[source].file != NULL) {
        (void)file_close(rows[source].file);
        rows[source].file = NULL;
    }
    if (rows[source].first == 0u) {
        rows[source].index = (uint16_t)(rows[source].index + 1u);
        if (rows[source].index >= SA_RECORD_FILE_MAX)
            rows[source].index = 0u;
    } else {
        rows[source].first = 0u;
    }
    service_audio_format_recording_path(source, rows[source].index, path, SA_PATH_LEN);
    rows[source].file = file_open(path, write_mode);
    if (rows[source].file == NULL) {
        SA_LOG0(1, fn, 0x146u, open_fail, open_fail_c);
        return -1;
    }
    rows[source].written = 0u;
    return 0;
}

/* Stock check_file_path: create /audio/ when it does not exist. */
void service_audio_recording_directory_prepare(void)
{
    static const char fn[] = "check_file_path"; /* ROM 0x788700 */
    static const char mkdir_fail[] = "Directory creation failed"; /* ROM 0x770c10 */
    static const char mkdir_fail_c[] = "[svc.audio]Directory creation failed"; /* ROM 0x74d8a4 */
    uint32_t info[SA_LFS_INFO_SIZE / 4u];

    if (lfs_stat_4cfa8a(audio_file_lfs_context, audio_dir, info) == SA_LFS_ERR_NOENT &&
        audio_file_lfs_mkdir_4cfc5c(audio_file_lfs_context, audio_dir) != 0)
        SA_LOG0(1, fn, 0x155u, mkdir_fail, mkdir_fail_c);
}

/* Reset the row and pick the first file index whose file is absent ("rb"
 * probe); the first open_next then reuses that index. */
void service_audio_recording_start(uint8_t source)
{
    static const char probe_mode[] = "rb"; /* inline literal-pool word 0x57b378 */
    char path[SA_PATH_LEN];

    if (source >= SA_SOURCE_COUNT)
        return;
    service_audio_recording_directory_prepare();
    sa_recording_t *rows = g2_audio_recording_rows_20073c08;
    (void)aeabi_memset_43c0e4(&rows[source], sizeof(rows[source]), 0);
    rows[source].first = 1u;
    (void)aeabi_memset_43c0e4(path, SA_PATH_LEN, 0);
    rows[source].index = 0u;
    while (rows[source].index < SA_RECORD_FILE_MAX) {
        service_audio_format_recording_path(source, rows[source].index, path, SA_PATH_LEN);
        void *probe = file_open(path, probe_mode);
        if (probe == NULL)
            break;
        (void)file_close(probe);
        rows[source].index = (uint16_t)(rows[source].index + 1u);
    }
    if (rows[source].index >= SA_RECORD_FILE_MAX)
        rows[source].index = 0u;
    rows[source].started = 1u;
}

/* Append PCM/LC3 bytes to the source's recording, rotating at 1 MiB. A short
 * write closes the file; the next call opens a new one. */
void SVC_PcmRecoderProcess(uint8_t source, const void *data, uint32_t bytes)
{
    static const char fn[] = "SVC_PcmRecoderProcess"; /* ROM 0x77b35c */
    static const char new_fail[] = "create new file failed"; /* ROM 0x77b374 */
    static const char new_fail_c[] = "[svc.audio]create new file failed"; /* ROM 0x7591d4 */
    static const char write_fail[] = "[PCM:%d] recording failed."; /* ROM 0x770c2c */
    static const char write_fail_c[] = "[svc.audio][PCM:%d] recording failed."; /* ROM 0x74d8cc */
    sa_recording_t *rows = g2_audio_recording_rows_20073c08;

    if (source >= SA_SOURCE_COUNT)
        return;
    if (rows[source].started == 0u)
        service_audio_recording_start(source);
    if ((rows[source].file == NULL || bytes + rows[source].written > SA_RECORD_FILE_LIMIT) &&
        service_audio_recording_open_next(source) != 0) {
        SA_LOG0(1, fn, 0x18au, new_fail, new_fail_c);
        return;
    }
    uint32_t written = file_write(data, 1u, bytes, rows[source].file);
    if (written == bytes) {
        rows[source].written = bytes + rows[source].written;
        return;
    }
    SA_LOGN(1, 1, fn, 0x197u, write_fail, write_fail_c, source);
    (void)file_close(rows[source].file);
    rows[source].file = NULL;
}

void service_audio_current_recording_path(uint8_t source, char *dst, uint32_t size)
{
    if (source < SA_SOURCE_COUNT)
        service_audio_format_recording_path(source, g2_audio_recording_rows_20073c08[source].index, dst, size);
}
