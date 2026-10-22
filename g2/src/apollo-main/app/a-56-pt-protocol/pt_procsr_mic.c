/* Product-test microphone recording handlers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c.
 * Native 0x570d40..0x571cb6: commands 0x19 enter_mic_recording_mode,
 * 0x1A exit_mic_recording_mode and 0x1B transfer_mic_recording_data (TSV labels
 * pt_cmd_18/19/1A_handler; the TSV command labels are shifted, the reply byte
 * always echoes the real command).
 *
 * Handler contract as in pt_procsr_device.c. Mic index (payload[4] for
 * 0x19/0x1A, payload[5] for 0x1B): 0 codec mic, 1 PDM mic, 2 GPIO 0x86
 * (codec pin) high/low, 3 forward start/stop to the peer arm over the
 * inter-arm UART (app 0x102). 0x1A loads the recording file named by
 * service_audio_current_recording_path into a heap cache (max 300 KB) and
 * returns it in 210-byte chunks (0x1B); payload[4] == 1 re-sends the previous chunk. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define PT_PRODUCT_TEST_MODE 1u
#define PT_STATUS_OK 0u
#define PT_STATUS_INVALID 3u
#define PT_STATUS_NOT_TEST_MODE 5u
#define PT_MIC_CODEC 0u
#define PT_MIC_PDM 1u
#define PT_MIC_GPIO 2u
#define PT_MIC_PEER 3u
#define PT_MIC_GPIO_PIN 0x86u
#define PT_PEER_UART_APP 0x102u
#define PT_CHUNK_SIZE 0xd2u
#define PT_CACHE_PATH_SIZE 0x20u
#define PT_CACHE_LIMIT 0x4b000 /* 300 KB */
#define PT_ROLE_MASTER 1u

/* Inter-arm UART request forwarded for mic index 3 (templates ROM 0x78bd50
 * start, 0x78bd5c stop). */
typedef struct {
    uint32_t action;     /* +0x0 1 start recording, 2 stop recording */
    uint8_t role;        /* +0x4 local device role */
    uint8_t target;      /* +0x5 peer role: 2 when local is master, else 1 */
    uint8_t pad6[2];
    uint32_t reserved;   /* +0x8 */
} pt_mic_peer_request_t;
_Static_assert(sizeof(pt_mic_peer_request_t) == 12, "peer mic request is 12 bytes");

extern uint8_t *g2_pt_audio_file_cache_200748d0;              /* RAM 0x200748d0 heap cache */
extern uint32_t g2_pt_audio_cache_size_200748d4;              /* RAM 0x200748d4 */
extern uint32_t g2_pt_audio_cache_offset_200748d8;            /* RAM 0x200748d8 */
extern uint32_t g2_pt_audio_last_chunk_200748cc;              /* RAM 0x200748cc */
extern uint8_t g2_pt_audio_cache_valid_20075006;              /* RAM 0x20075006 */
extern char g2_pt_audio_cache_path_2007393c[PT_CACHE_PATH_SIZE]; /* RAM 0x2007393c */

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len); /* memcpy 0x439be4 */
extern char *g2_strcpy_48d540(char *dst, const char *src);
extern int32_t string_compare_46cacc(const char *a, const char *b);            /* strcmp */
extern uint8_t productModeGet(void);                                           /* 0x4abe60 */
extern int32_t production_codec_mic_func_init(uint8_t channels);               /* 0x58f69a */
extern int32_t production_codec_mic_func_deinit(void);                         /* 0x58f74a */
extern int32_t production_pdm_mic_func_init(void);                             /* 0x58f7b0 */
extern int32_t production_pdm_mic_func_deinit(void);                           /* 0x58f806 */
extern uint32_t g2_codec_pin_write(uint32_t pin, uint32_t value);              /* 0x53a5be */
extern uint32_t display_driver_uled_mode_45a568(void);                         /* device role, 1 master */
extern uint32_t audio_uart_request_send(uint32_t, const void *, uint32_t, uint32_t); /* 0x4651e0 */
extern void service_audio_current_recording_path(uint8_t index, char *path, uint32_t size); /* 0x57b352 */
extern void *file_open(const char *path, const char *mode);                    /* 0x474550 */
extern int32_t file_close(void *file);                                         /* 0x4745f4 */
extern uint32_t file_read(void *buffer, uint32_t size, uint32_t count, void *file); /* 0x474634 */
extern void *file_heap_allocate(uint32_t);                                     /* 0x474cd2 */
extern void file_heap_free(void *);                                            /* 0x474d16 */
extern int32_t get_file_size_by_fp_56f23a(void *file);                         /* pt_protocol_procsr.c */

static const char module_tag[] = "pt_protocol_procsr"; /* ROM 0x7829fc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\pt_protocol_procsr.c"; /* ROM 0x6ef458 */
static const char para_null[] = "%s para is NULL\n"; /* ROM 0x782a74 */
static const char para_null_c[] = "[pt_protocol_procsr]%s para is NULL\n"; /* ROM 0x74d304 */
static const char denied[] = "permission denied current mode is not product test mode"; /* ROM 0x721c18 */
static const char denied_c[] = "[pt_protocol_procsr]permission denied current mode is not product test mode"; /* ROM 0x6f586c */
static const pt_mic_peer_request_t peer_start = {1u, 0u, 0u, {0u, 0u}, 0u}; /* ROM 0x78bd50 */
static const pt_mic_peer_request_t peer_stop = {2u, 0u, 0u, {0u, 0u}, 0u};  /* ROM 0x78bd5c */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

#define PT_CLOG(level, nargs) (((uint32_t)(level) << 26) | ((uint32_t)(nargs) << 22))
#define PT_LOG0(level, fn, line, fmt, cfmt) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt)); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), 0), (cfmt), (cfmt)); \
    } while (0)
#define PT_LOGN(level, nargs, fn, line, fmt, cfmt, ...) do { \
        if (log_extended_on()) audio_log_extended((level), module_tag, source_file, (fn), (line), (fmt), __VA_ARGS__); \
        if (log_compressed_on()) (void)compress_log_output(PT_CLOG((level), (nargs)), (cfmt), (cfmt), __VA_ARGS__); \
    } while (0)
#define PT_BAD_ARGS(payload, length, rsp, rsp_len, min) \
    ((rsp) == NULL || (rsp_len) == NULL || (payload) == NULL || (uint8_t)(length) < (min))
#define PT_HEADER(rsp, idx, rsp_cmd, data_len) do { \
        (rsp)[(idx)++] = (rsp_cmd); \
        (rsp)[(idx)++] = 1u; \
        (rsp)[(idx)++] = 3u; \
        (rsp)[(idx)++] = (data_len); \
    } while (0)

/* Both enter and exit drop any cached recording first. */
#define PT_CACHE_RESET() do { \
        if (g2_pt_audio_file_cache_200748d0 != NULL) { \
            file_heap_free(g2_pt_audio_file_cache_200748d0); \
            g2_pt_audio_file_cache_200748d0 = NULL; \
        } \
        g2_pt_audio_cache_valid_20075006 = 0u; \
        g2_pt_audio_cache_size_200748d4 = 0u; \
        g2_pt_audio_cache_offset_200748d8 = 0u; \
        (void)aeabi_memset_43c0e4(g2_pt_audio_cache_path_2007393c, PT_CACHE_PATH_SIZE, 0); \
    } while (0)

/* Forward start/stop to the peer arm (inlined by stock in both handlers). */
#define PT_MIC_PEER_FORWARD(template_request) do { \
        pt_mic_peer_request_t request = (template_request); \
        request.role = (uint8_t)display_driver_uled_mode_45a568(); \
        request.target = display_driver_uled_mode_45a568() == PT_ROLE_MASTER ? 2u : 1u; \
        (void)audio_uart_request_send(PT_PEER_UART_APP, &request, sizeof request, 0u); \
    } while (0)

/* Command 0x19 (TSV label pt_cmd_18_handler): payload[4] = mic index, payload[5] = codec channel count. */
uint32_t pt_cmd_18_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "enter_mic_recording_mode"; /* ROM 0x770548 */
    static const char join[] = "join in enter_mic_recording_mode, index = %d"; /* ROM 0x737334 */
    static const char join_c[] = "[pt_protocol_procsr]join in enter_mic_recording_mode, index = %d"; /* ROM 0x704c54 */
    static const char begin[] = "mic begin recording"; /* ROM 0x782b28 */
    static const char begin_c[] = "[pt_protocol_procsr]mic begin recording"; /* ROM 0x74d37c */
    static const char high[] = "GPIO%d set to HIGH"; /* ROM 0x782b3c */
    static const char high_c[] = "[pt_protocol_procsr]GPIO%d set to HIGH"; /* ROM 0x74d3a4 */
    static const char invalid[] = "%s para is invalid\n"; /* ROM 0x782b50 */
    static const char invalid_c[] = "[pt_protocol_procsr]%s para is invalid\n"; /* ROM 0x74d3cc */

    PT_CACHE_RESET();
    PT_LOGN(3, 1, fn, 0x54fu, join, join_c, payload[4]);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 6u)) {
        PT_LOGN(1, 1, fn, 0x552u, para_null, para_null_c, fn);
        return 0xffffffffu; /* -1 */
    }
    uint8_t mic = payload[4];
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x19u, 2u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        PT_LOG0(3, fn, 0x561u, begin, begin_c);
        if (mic == PT_MIC_CODEC) {
            (void)production_codec_mic_func_init(payload[5]);
        } else if (mic == PT_MIC_PDM) {
            (void)production_pdm_mic_func_init();
        } else if (mic == PT_MIC_GPIO) {
            (void)g2_codec_pin_write(PT_MIC_GPIO_PIN, 1u);
            PT_LOGN(3, 1, fn, 0x56eu, high, high_c, PT_MIC_GPIO_PIN);
        } else if (mic == PT_MIC_PEER) {
            PT_MIC_PEER_FORWARD(peer_start);
        } else {
            PT_LOGN(1, 1, fn, 0x57du, invalid, invalid_c, fn);
            rsp[idx++] = PT_STATUS_INVALID;
            rsp[idx++] = mic;
            *rsp_len = idx;
            return 0;
        }
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_LOG0(1, fn, 0x588u, denied, denied_c);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    rsp[idx++] = mic;
    *rsp_len = idx;
    return 0;
}

/* Command 0x1A (TSV label pt_cmd_19_handler): payload[4] = mic index. */
uint32_t pt_cmd_19_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "exit_mic_recording_mode"; /* ROM 0x77acfc */
    static const char join[] = "join in exit_mic_recording_mode, index = %d"; /* ROM 0x742020 */
    static const char join_c[] = "[pt_protocol_procsr]join in exit_mic_recording_mode, index = %d"; /* ROM 0x70e264 */
    static const char done[] = "mic exit recording"; /* ROM 0x782b64 */
    static const char done_c[] = "[pt_protocol_procsr]mic exit recording"; /* ROM 0x74d3f4 */
    static const char low[] = "GPIO%d set to LOW"; /* ROM 0x782b78 */
    static const char low_c[] = "[pt_protocol_procsr]GPIO%d set to LOW"; /* ROM 0x74d41c */

    PT_CACHE_RESET();
    PT_LOGN(3, 1, fn, 0x59fu, join, join_c, payload[4]);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 5u)) {
        PT_LOGN(1, 1, fn, 0x5a2u, para_null, para_null_c, fn);
        return 0xffffffffu; /* -1 */
    }
    uint8_t mic = payload[4];
    uint8_t idx = 0;
    PT_HEADER(rsp, idx, 0x1au, 2u);
    if (productModeGet() == PT_PRODUCT_TEST_MODE) {
        PT_LOG0(3, fn, 0x5b2u, done, done_c);
        if (mic == PT_MIC_CODEC) {
            (void)production_codec_mic_func_deinit();
        } else if (mic == PT_MIC_PDM) {
            (void)production_pdm_mic_func_deinit();
        } else if (mic == PT_MIC_GPIO) {
            (void)g2_codec_pin_write(PT_MIC_GPIO_PIN, 0u);
            PT_LOGN(3, 1, fn, 0x5bfu, low, low_c, PT_MIC_GPIO_PIN);
        } else if (mic == PT_MIC_PEER) {
            PT_MIC_PEER_FORWARD(peer_stop);
        } else {
            PT_LOGN(1, 1, fn, 0x5ceu, para_null, para_null_c, fn);
            rsp[idx++] = PT_STATUS_INVALID;
            rsp[idx++] = mic;
            *rsp_len = idx;
            return 0;
        }
        rsp[idx++] = PT_STATUS_OK;
    } else {
        PT_LOG0(1, fn, 0x5d9u, denied, denied_c);
        rsp[idx++] = PT_STATUS_NOT_TEST_MODE;
    }
    rsp[idx++] = payload[4];
    *rsp_len = idx;
    return 0;
}

/* Command 0x1B (TSV label pt_cmd_1A_handler) reply 0x1b, 220 bytes: [4] mic index, [5..8] big-endian byte sum of
 * the whole frame except [5..8], [9] 1 on the last chunk, [10..219] data.
 * Failures reply with the 6-byte form status 3 (or 5 outside test mode). */
uint32_t pt_cmd_1A_handler(const uint8_t *payload, uint8_t length, uint8_t *rsp, uint8_t *rsp_len)
{
    static const char fn[] = "transfer_mic_recording_data"; /* ROM 0x770564 */
    static const char join[] = "join in transfer_mic_recording_data, index = %d"; /* ROM 0x737364 */
    static const char join_c[] = "[pt_protocol_procsr]join in transfer_mic_recording_data, index = %d"; /* ROM 0x704c98 */
    static const char not_prod[] = "transfer_mic_recording_data error mode is not production mode"; /* ROM 0x70e2a4 */
    static const char not_prod_c[] = "[pt_protocol_procsr]transfer_mic_recording_data error mode is not production mode"; /* ROM 0x6e9700 */
    static const char mic_index[] = "mic index = %d"; /* ROM 0x788450 */
    static const char mic_index_c[] = "[pt_protocol_procsr]mic index = %d"; /* ROM 0x758b14 */
    static const char read_mode[] = "rb"; /* ROM 0x571908 (literal pool) */
    static const char open_fail[] = "Failed to open file %s"; /* ROM 0x77ad14 */
    static const char open_fail_c[] = "[pt_protocol_procsr]Failed to open file %s"; /* ROM 0x74204c */
    static const char size_msg[] = "mic file '%s' size=%ld bytes"; /* ROM 0x764370 */
    static const char size_msg_c[] = "[pt_protocol_procsr]mic file '%s' size=%ld bytes"; /* ROM 0x72c4ac */
    static const char bad_size[] = "Invalid file size: %ld for %s"; /* ROM 0x764390 */
    static const char bad_size_c[] = "[pt_protocol_procsr]Invalid file size: %ld for %s"; /* ROM 0x72c4e0 */
    static const char too_big[] = "File size %ld exceeds 300KB limit"; /* ROM 0x758b38 */
    static const char too_big_c[] = "[pt_protocol_procsr]File size %ld exceeds 300KB limit"; /* ROM 0x721c50 */
    static const char alloc_msg[] = "allocating audio_file_cache, size=%u"; /* ROM 0x74d444 */
    static const char alloc_msg_c[] = "[pt_protocol_procsr]allocating audio_file_cache, size=%u"; /* ROM 0x717e9c */
    static const char alloc_fail[] = "Failed to allocate memory for file cache, size: %ld"; /* ROM 0x72c514 */
    static const char alloc_fail_c[] = "[pt_protocol_procsr]Failed to allocate memory for file cache, size: %ld"; /* ROM 0x6fc38c */
    static const char fread_msg[] = "fread returned %u bytes"; /* ROM 0x77ad2c */
    static const char fread_msg_c[] = "[pt_protocol_procsr]fread returned %u bytes"; /* ROM 0x742078 */
    static const char short_read[] = "Failed to read complete file, expected %ld, got %zu"; /* ROM 0x72c548 */
    static const char short_read_c[] = "[pt_protocol_procsr]Failed to read complete file, expected %ld, got %zu"; /* ROM 0x6fc3d4 */
    static const char loaded[] = "File %s loaded to cache, size: %ld bytes"; /* ROM 0x7420a4 */
    static const char loaded_c[] = "[pt_protocol_procsr]File %s loaded to cache, size: %ld bytes"; /* ROM 0x70e2e4 */
    static const char retry[] = "audio data transf failed, seeking back in cache"; /* ROM 0x737394 */
    static const char retry_c[] = "[pt_protocol_procsr]audio data transf failed, seeking back in cache"; /* ROM 0x704cdc */
    static const char rewind[] = "Cannot seek before cache start, reset to beginning"; /* ROM 0x72c57c */
    static const char rewind_c[] = "[pt_protocol_procsr]Cannot seek before cache start, reset to beginning"; /* ROM 0x6fc41c */
    static const char finished[] = "audio data transf finish, total bytes: %d"; /* ROM 0x7420d0 */
    static const char finished_c[] = "[pt_protocol_procsr]audio data transf finish, total bytes: %d"; /* ROM 0x70e324 */
    static const char remaining[] = "audio data transf not finish, remaining bytes: %d"; /* ROM 0x72c5b0 */
    static const char remaining_c[] = "[pt_protocol_procsr]audio data transf not finish, remaining bytes: %d"; /* ROM 0x6fc464 */
    char path[PT_CACHE_PATH_SIZE];
    uint8_t chunk[PT_CHUNK_SIZE];

    PT_LOGN(3, 1, fn, 0x5e6u, join, join_c, payload[5]);
    if (PT_BAD_ARGS(payload, length, rsp, rsp_len, 6u)) {
        PT_LOGN(1, 1, fn, 0x5e9u, para_null, para_null_c, fn);
        return 0xffffffffu; /* -1 */
    }
    (void)aeabi_memset_43c0e4(chunk, PT_CHUNK_SIZE, 0);
    uint32_t sum = 0;
    uint8_t mic = payload[5];
    if (productModeGet() != PT_PRODUCT_TEST_MODE) {
        PT_LOG0(1, fn, 0x5f4u, not_prod, not_prod_c);
        rsp[0] = 0x1bu;
        rsp[1] = 1u;
        rsp[2] = 3u;
        rsp[3] = 2u;
        rsp[4] = PT_STATUS_NOT_TEST_MODE;
        rsp[5] = mic;
        *rsp_len = 6u;
        return 0;
    }
    rsp[0] = 0x1bu;
    rsp[1] = 1u;
    rsp[2] = 3u;
    rsp[3] = 0xd8u;
    rsp[4] = mic;
    PT_LOGN(3, 1, fn, 0x605u, mic_index, mic_index_c, mic);
    (void)aeabi_memset_43c0e4(path, PT_CACHE_PATH_SIZE, 0);
    service_audio_current_recording_path(mic, path, PT_CACHE_PATH_SIZE);

    if (g2_pt_audio_cache_valid_20075006 == 0u || string_compare_46cacc(path, g2_pt_audio_cache_path_2007393c) != 0) {
        if (g2_pt_audio_file_cache_200748d0 != NULL) {
            file_heap_free(g2_pt_audio_file_cache_200748d0);
            g2_pt_audio_file_cache_200748d0 = NULL;
        }
        g2_pt_audio_cache_valid_20075006 = 0u;
        g2_pt_audio_cache_offset_200748d8 = 0u;
        g2_pt_audio_cache_size_200748d4 = 0u;
        void *file = file_open(path, read_mode);
        if (file == NULL) {
            PT_LOGN(1, 1, fn, 0x61fu, open_fail, open_fail_c, path);
            goto fail;
        }
        int32_t size = get_file_size_by_fp_56f23a(file);
        PT_LOGN(3, 2, fn, 0x62du, size_msg, size_msg_c, path, size);
        if (size < 1) {
            PT_LOGN(1, 2, fn, 0x630u, bad_size, bad_size_c, size, path);
            (void)file_close(file);
            goto fail;
        }
        if (size >= PT_CACHE_LIMIT + 1) {
            PT_LOGN(1, 1, fn, 0x63fu, too_big, too_big_c, size);
            (void)file_close(file);
            goto fail;
        }
        PT_LOGN(3, 1, fn, 0x64eu, alloc_msg, alloc_msg_c, (uint32_t)size);
        g2_pt_audio_file_cache_200748d0 = file_heap_allocate((uint32_t)size);
        if (g2_pt_audio_file_cache_200748d0 == NULL) {
            PT_LOGN(1, 1, fn, 0x652u, alloc_fail, alloc_fail_c, size);
            (void)file_close(file);
            goto fail;
        }
        uint32_t got = file_read(g2_pt_audio_file_cache_200748d0, 1u, (uint32_t)size, file);
        PT_LOGN(3, 1, fn, 0x661u, fread_msg, fread_msg_c, got);
        (void)file_close(file);
        if (got != (uint32_t)size) {
            PT_LOGN(1, 2, fn, 0x665u, short_read, short_read_c, size, got);
            file_heap_free(g2_pt_audio_file_cache_200748d0);
            g2_pt_audio_file_cache_200748d0 = NULL;
            goto fail;
        }
        g2_pt_audio_cache_size_200748d4 = (uint32_t)size;
        g2_pt_audio_cache_offset_200748d8 = 0u;
        g2_pt_audio_cache_valid_20075006 = 1u;
        (void)g2_strcpy_48d540(g2_pt_audio_cache_path_2007393c, path);
        PT_LOGN(3, 2, fn, 0x679u, loaded, loaded_c, path, size);
    }

    if (payload[4] == 1u) {
        PT_LOG0(4, fn, 0x680u, retry, retry_c);
        if (g2_pt_audio_cache_offset_200748d8 < PT_CHUNK_SIZE) {
            g2_pt_audio_cache_offset_200748d8 = 0u;
            PT_LOG0(2, fn, 0x686u, rewind, rewind_c);
        } else {
            g2_pt_audio_cache_offset_200748d8 -= PT_CHUNK_SIZE;
        }
    }
    uint32_t n = PT_CHUNK_SIZE;
    if (g2_pt_audio_cache_size_200748d4 < g2_pt_audio_cache_offset_200748d8 + PT_CHUNK_SIZE)
        n = g2_pt_audio_cache_size_200748d4 - g2_pt_audio_cache_offset_200748d8;
    if (n == 0u) {
        (void)aeabi_memset_43c0e4(chunk, PT_CHUNK_SIZE, 0);
    } else {
        (void)audio_queue_copy_bytes(chunk, g2_pt_audio_file_cache_200748d0 + g2_pt_audio_cache_offset_200748d8, n);
        g2_pt_audio_cache_offset_200748d8 += n;
    }
    g2_pt_audio_last_chunk_200748cc = n;
    (void)audio_queue_copy_bytes(rsp + 10, chunk, PT_CHUNK_SIZE);
    if (g2_pt_audio_cache_offset_200748d8 < g2_pt_audio_cache_size_200748d4) {
        rsp[9] = 0u;
        PT_LOGN(3, 1, fn, 0x6afu, remaining, remaining_c,
                g2_pt_audio_cache_size_200748d4 - g2_pt_audio_cache_offset_200748d8);
    } else {
        rsp[9] = 1u;
        if (g2_pt_audio_file_cache_200748d0 != NULL) {
            file_heap_free(g2_pt_audio_file_cache_200748d0);
            g2_pt_audio_file_cache_200748d0 = NULL;
        }
        g2_pt_audio_cache_valid_20075006 = 0u;
        g2_pt_audio_cache_size_200748d4 = 0u;
        g2_pt_audio_cache_offset_200748d8 = 0u;
        (void)aeabi_memset_43c0e4(g2_pt_audio_cache_path_2007393c, PT_CACHE_PATH_SIZE, 0);
        /* Logged after the reset, so the stock total is always 0. */
        PT_LOGN(3, 1, fn, 0x6aau, finished, finished_c, g2_pt_audio_cache_size_200748d4);
    }
    for (int i = 0; i < 0xdc; i++) {
        if ((uint32_t)(i - 5) > 3u)
            sum += rsp[i];
    }
    rsp[5] = (uint8_t)(sum >> 24);
    rsp[6] = (uint8_t)(sum >> 16);
    rsp[7] = (uint8_t)(sum >> 8);
    rsp[8] = (uint8_t)sum;
    *rsp_len = 0xdcu;
    return 0;

fail:
    rsp[0] = 0x1bu;
    rsp[1] = 1u;
    rsp[2] = 3u;
    rsp[3] = 2u;
    rsp[4] = PT_STATUS_INVALID;
    rsp[5] = mic;
    *rsp_len = 6u;
    return 0;
}
