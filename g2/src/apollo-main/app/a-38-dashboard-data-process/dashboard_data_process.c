/* Stock D:\01_workspace\s200_ap510b_iar_git\platform\protocols\dashboard_service\dashboard_data_process.c
 * (log tag "dashboard_data_process"), protobuf side of the dashboard service.
 * Native 0x4FDD6E..0x4FDF07, 0x4FE0AA..0x4FE2C1, 0x4FE318..0x4FEC01,
 * 0x4FEC14..0x4FEC7F, 0x4FEC98..0x4FEDBF, 0x4FEDCC..0x4FEEDF, 0x4FEF04..0x4FF089,
 * 0x4FF09C..0x4FF1BD; literal pools 0x4FE2C4..0x4FE317, 0x4FEC04..0x4FEC13,
 * 0x4FEC80..0x4FEC97, 0x4FEDC0..0x4FEDCB, 0x4FEEE0..0x4FEF03, 0x4FF08C..0x4FF09B,
 * 0x4FF1C0..0x4FF213 (shared with later functions), 0x4FF494..0x4FF4BF.
 *
 * One DashboardDataPackage message (nanopb, RAM 0x200566c8, descriptor ROM
 * 0x77610c) is reused for every decode and encode. Header: command_id u8 +0,
 * magic_random u32 +4, which_payload u16 +8, payload union from +0x10.
 *
 *   which  dir   command  meaning
 *   3      out   1        respond to app {+0x10 settings id, +0x14 result}
 *   4      in    -        display settings / weather / widget data / u32 at +0x14ac
 *   6      out   3        send to app (notification status, widget state, raw 64 B)
 *   7      in    -        {+0x10 == 1} request news info (+0x14b8)
 *   8      out   6        respond NewsInfo {+0x10 = 0x55aa}
 *   9      in    7        request news info -> reply which 10 / command 8
 *   0x0b   in    9        SendNewsData session record -> reply which 12 / command 10
 *   0x0d   out   0x0b     request app to upgrade news info
 *   0x0e   out   0x0c     notify app of news status {+0x10 status u8, +0x14 index}
 *   0x0f   in    0x0d     clear all data -> reply which 0x10 / command 0x0e
 *
 * The send-to-app encoder compares two floats against 0, so the unit needs
 * single-precision VFP (profile g2-apollo-main-3). No float crosses a call. */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* nanopb 0.4.9 streams (PB_NO_ERRMSG not set). */
typedef struct g2_pb_ostream {
    bool (*callback)(struct g2_pb_ostream *stream, const uint8_t *buf, size_t count);
    void *state;
    size_t max_size;
    size_t bytes_written; /* +0x0c */
    const char *errmsg;   /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "pb_ostream_t ABI");

typedef struct g2_pb_istream {
    bool (*callback)(struct g2_pb_istream *stream, uint8_t *buf, size_t count);
    void *state;
    size_t bytes_left;
    const char *errmsg;   /* +0x0c */
} g2_pb_istream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "pb_istream_t ABI");

/* DashboardDataPackage (decoded union is wider than any single member). */
typedef struct {
    uint8_t command_id;       /* +0x00 */
    uint8_t pad_01[3];
    uint32_t magic_random;    /* +0x04 */
    uint16_t which_payload;   /* +0x08 */
    uint8_t pad_0a[6];
    uint8_t payload[0xcf0];   /* +0x10, at least up to +0xd00 (cleared by the reset) */
} g2_dashboard_package_t;
_Static_assert(offsetof(g2_dashboard_package_t, payload) == 0x10u, "payload union at +0x10");

/* Message given to dashboard_send_to_app_serialize (see ui/a-15-dashboard). */
typedef struct {
    uint32_t package_id;     /* +0x00 */
    uint8_t flag;            /* +0x04 */
    uint8_t data_type;       /* +0x05 1 status, 2 widget state, 3 raw 64 bytes */
    uint8_t reserved_06[2];
    uint32_t payload[18];    /* +0x08 */
} g2_dashboard_app_msg_t;
_Static_assert(sizeof(g2_dashboard_app_msg_t) == 0x50u, "dashboard app message");

/* One news session (0x1ca8 bytes), five in g2_news_staging_203024a4. */
typedef struct {
    uint8_t valid;            /* +0x0000 */
    uint8_t pad_01[3];
    uint32_t session_id;      /* +0x0004 */
    uint32_t field_08;        /* +0x0008 */
    uint32_t news_index;      /* +0x000c */
    uint32_t news_id;         /* +0x0010 listed in the NewsInfo reply */
    char text_14[0x80];       /* +0x0014 */
    char text_94[0x80];       /* +0x0094 */
    char body[0x1b8a];        /* +0x0114 */
    uint8_t pad_1c9e[2];
    uint32_t stamp[2];        /* +0x1ca0 */
} g2_news_session_t;
_Static_assert(sizeof(g2_news_session_t) == 0x1ca8u, "news session record");

#define NEWS_SESSION_MAX 5u

/* Parsed package (caller buffer, 0x14c0 bytes) offsets. */
#define PARSED_SETTINGS     0x1480u /* display settings copy */
#define PARSED_WORD_14AC    0x14acu
#define PARSED_HAS_SETTINGS 0x14b6u
#define PARSED_HAS_14AC     0x14b7u
#define PARSED_REQ_NEWS     0x14b8u
#define PARSED_NEWS_V2      0x14b9u

/* Field access inside the package payload and the parsed buffer. */
#define P8(b, o)  (*(uint8_t *)((uint8_t *)(b) + (o)))
#define P16(b, o) (*(uint16_t *)(void *)((uint8_t *)(b) + (o)))
#define P32(b, o) (*(uint32_t *)(void *)((uint8_t *)(b) + (o)))
#define P64(b, o) (*(uint64_t *)(void *)((uint8_t *)(b) + (o)))
#define PF(b, o)  (*(float *)(void *)((uint8_t *)(b) + (o)))
#define PKG_FIELD8(o)  P8(&g2_dashboard_package, (o))
#define PKG_FIELD16(o) P16(&g2_dashboard_package, (o))
#define PKG_FIELD32(o) P32(&g2_dashboard_package, (o))
#define PKG_FIELD64(o) P64(&g2_dashboard_package, (o))

#define WAIT_FOREVER 0xffffffffu
#define PB_TX_SIZE   0x100u

/* RAM state. */
extern g2_dashboard_package_t g2_dashboard_package;     /* RAM 0x200566c8 */
extern uint8_t g2_dashboard_tx_buffer[PB_TX_SIZE];      /* RAM 0x200702ec */
extern uint32_t g2_dashboard_last_command_id;           /* RAM 0x20074408 */
extern uint32_t g2_dashboard_last_magic;                /* RAM 0x2007440c */
extern uint32_t g2_dashboard_settings_id;               /* RAM 0x20074410 */
extern uint8_t *g2_dashboard_payload_ptr;               /* RAM 0x20074414 */
extern uint8_t *g2_dashboard_settings_src;              /* RAM 0x20074418 */
extern uint8_t *g2_dashboard_settings_dst;              /* RAM 0x2007441c */
extern uint8_t *g2_dashboard_widget_ptr;                /* RAM 0x20074420 */
extern uint8_t *g2_dashboard_weather_ptr;               /* RAM 0x20074424 */
extern uint8_t *g2_dashboard_widget_data_ptr;           /* RAM 0x20074428 */
extern uint8_t *g2_dashboard_word_ptr;                  /* RAM 0x2007442c */
extern uint8_t g2_news_staging_203024a4[0x8f48];        /* RAM 0x203024a4 */
extern void *g2_dashboard_mutex_200743a8;               /* RAM 0x200743a8 osMutexId */
extern const uint8_t g2_dashboard_package_fields[];     /* ROM 0x77610c pb_msgdesc_t */

/* nanopb (upstream names). */
extern g2_pb_ostream_t pb_ostream_from_buffer(uint8_t *buf, size_t bufsize);   /* 0x4905f4 */
extern bool pb_encode(g2_pb_ostream_t *stream, const void *fields, const void *src); /* 0x490c32 */
extern g2_pb_istream_t pb_istream_from_buffer(const uint8_t *buf, size_t msglen); /* 0x48f49c */
extern bool pb_decode(g2_pb_istream_t *stream, const void *fields, void *dest); /* 0x490120 */

/* Runtime. */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);   /* memcpy 0x439be4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                     /* 0x44981c */
extern void audio_uart_task_delay(uint32_t ticks);              /* 0x454b4c */
extern uint32_t audio_uart_service_mode(void);                  /* 0x45a570, 1 = master */
extern uint32_t audio_log_wake_allowed(void);                   /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern int32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                 uint32_t flags); /* 0x464bb2 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload,
                                    uint16_t length); /* 0x475b14 */
extern uint32_t Thread_MsgPbNotifyByBle(uint8_t type, uint8_t command, const void *payload,
                                        uint16_t length); /* 0x475c1a */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* Same TU, outside this unit. */
extern void dashboard_parsed_data_reset_4fd93c(uint8_t *parsed);
extern uint32_t dashboard_parse_weather_4fda24(const uint8_t *weather, uint8_t *parsed);
extern uint32_t dashboard_parse_widget_data_4fdad4(const uint8_t *widget, uint8_t *parsed);

void dashboard_package_reset_4fdd6e(g2_dashboard_package_t *pkg);
uint32_t requesetAppUpgradeNewsInfo_4fe0aa(void);
uint32_t notifyAppNewsStatus_4fe1b4(uint8_t status, uint32_t index);
uint8_t dashboard_parse_data_package_4fe318(const uint8_t *data, uint32_t length, uint8_t *parsed);
uint32_t dashboard_respond_encode_4fec14(uint8_t result, uint8_t *buf, uint32_t *len);
uint32_t dashboard_respond_to_app_serialize_4fec98(uint32_t ret);
uint32_t dashboard_respond_NewsInfo_to_app_4fedcc(uint32_t ret);
uint32_t dashboard_send_to_app_serialize_internal_4fef04(const g2_dashboard_app_msg_t *msg,
                                                         uint8_t *buf, uint32_t *len);
uint32_t dashboard_send_to_app_serialize_4ff09c(const g2_dashboard_app_msg_t *msg);

static const char tag[] = "dashboard_data_process"; /* ROM 0x776424 */
static const char src[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\dashboard_service\\dashboard_data_process.c"; /* ROM 0x6da4e4 */
static const char none_text[] = "(none)"; /* ROM 0x78d2bc */
static const char fn_upgrade[] = "requesetAppUpgradeNewsInfo"; /* ROM 0x76aa10 */
static const char fn_status[] = "notifyAppNewsStatus"; /* ROM 0x77eba4 */
static const char m_upgrade[] = "requesetAppUpgradeNewsInfo to app"; /* ROM 0x753258 */
static const char t_upgrade[] = "[dashboard_data_process]requesetAppUpgradeNewsInfo to app"; /* ROM 0x713c48 */
static const char m_news_encode[] = "SendNewsData response encode failed: %s"; /* ROM 0x748d2c */
static const char t_news_encode[] =
    "[dashboard_data_process]SendNewsData response encode failed: %s"; /* ROM 0x70a764 */
static const char fn_parse[] = "dashboard_parse_data_package"; /* ROM 0x75f010 */
static const char m_bad_param[] = "Invalid parameters! data=%p, parsed_data=%p\n"; /* ROM 0x732bc4 */
static const char t_bad_param[] =
    "[dashboard_data_process]Invalid parameters! data=%p, parsed_data=%p\n"; /* ROM 0x6f98cc */
static const char m_decode[] = "decode failed: %s\n"; /* ROM 0x77ebb8 */
static const char t_decode[] = "[dashboard_data_process]decode failed: %s\n"; /* ROM 0x73d76c */
static const char m_clear_cmd[] =
    "DashboardDataPackage_ResClearAllData_tag command_id is not eDashboardCommandId_APP_REQUEST_CLEAR_ALL_DATA"; /* ROM 0x6a8454 */
static const char t_clear_cmd[] =
    "[dashboard_data_process]DashboardDataPackage_ResClearAllData_tag command_id is not eDashboardCommandId_APP_REQUEST_CLEAR_ALL_DATA"; /* ROM 0x6d4c28 */
static const char m_news_cmd[] =
    "DashboardDataPackage_ReqNewsInfo_tag command_id is not eDashboardCommandId_APP_REQUEST_NEWS_INFO"; /* ROM 0x6da548 */
static const char t_news_cmd[] =
    "[dashboard_data_process]DashboardDataPackage_ReqNewsInfo_tag command_id is not eDashboardCommandId_APP_REQUEST_NEWS_INFO"; /* ROM 0x633f8c */
static const char m_send_cmd[] = "SendNewsData command_id mismatch, expected %d, got %d"; /* ROM 0x71d688 */
static const char t_send_cmd[] =
    "[dashboard_data_process]SendNewsData command_id mismatch, expected %d, got %d"; /* ROM 0x6ec938 */
static const char m_no_news[] = "no news, special handling...."; /* ROM 0x75f030 */
static const char t_no_news[] = "[dashboard_data_process]no news, special handling...."; /* ROM 0x71d6c0 */
static const char m_master[] = "master role, send event to UI application"; /* ROM 0x73d798 */
static const char t_master[] =
    "[dashboard_data_process]master role, send event to UI application"; /* ROM 0x7019dc */
static const char m_range[] = "session_news_index %d out of range (max %d)"; /* ROM 0x73d7c4 */
static const char t_range[] =
    "[dashboard_data_process]session_news_index %d out of range (max %d)"; /* ROM 0x701a20 */
static const char m_news_sent[] = "SendNewsData response sent, news_status=%d, ret=%d"; /* ROM 0x728448 */
static const char t_news_sent[] =
    "[dashboard_data_process]SendNewsData response sent, news_status=%d, ret=%d"; /* ROM 0x6f29d0 */
static const char m_unsupported[] = "Unsupported command type: %d\n"; /* ROM 0x75f050 */
static const char t_unsupported[] =
    "[dashboard_data_process]Unsupported command type: %d\n"; /* ROM 0x71d6f8 */
static const char fn_respond[] = "dashboard_respond_to_app_serialize"; /* ROM 0x75327c */
static const char m_cmd_invalid[] =
    "dashboard respond to app serialize, command_id is invalid (0)"; /* ROM 0x70a7a4 */
static const char t_cmd_invalid[] =
    "[dashboard_data_process]dashboard respond to app serialize, command_id is invalid (0)"; /* ROM 0x6e2d28 */
static const char m_deprecated[] =
    "news protocol has been deprecated, please use the new news protocol"; /* ROM 0x701a64 */
static const char t_deprecated[] =
    "[dashboard_data_process]news protocol has been deprecated, please use the new news protocol"; /* ROM 0x6dfea0 */
static const char m_respond_failed[] = "dashboard respond to app serialize failed"; /* ROM 0x73d7f0 */
static const char t_respond_failed[] =
    "[dashboard_data_process]dashboard respond to app serialize failed"; /* ROM 0x701aa8 */
static const char fn_newsinfo[] = "dashboard_respond_NewsInfo_to_app"; /* ROM 0x7532a0 */
static const char fn_send_internal[] = "dashboard_send_to_app_serialize_internal"; /* ROM 0x73d81c */
static const char m_send_encode[] = "dashboard send to app serialize, pb_encode failed"; /* ROM 0x72847c */
static const char t_send_encode[] =
    "[dashboard_data_process]dashboard send to app serialize, pb_encode failed"; /* ROM 0x6f2a1c */
static const char fn_send[] = "dashboard_send_to_app_serialize"; /* ROM 0x75f070 */
static const char m_send_null[] = "dashboard send to app serialize, send_data is NULL"; /* ROM 0x7284b0 */
static const char t_send_null[] =
    "[dashboard_data_process]dashboard send to app serialize, send_data is NULL"; /* ROM 0x6f2a68 */
static const char m_ble_fail[] = "dashboard send to app serialize, BLE fail code = %d"; /* ROM 0x7284e4 */
static const char t_ble_fail[] =
    "[dashboard_data_process]dashboard send to app serialize, BLE fail code = %d"; /* ROM 0x6f2ab4 */

/* Stock log macro expansion; the compressed record flags carry the level in
 * bits 26..28 and the argument count in bits 22..25. */
#define DP_LOG(lvl, fn, line, nargs, m, t, ...)                                              \
    do {                                                                                     \
        if ((audio_log_flags() & 2u) != 0u)                                                  \
            audio_log_extended((lvl), tag, src, (fn), (line), (m), ##__VA_ARGS__);           \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                \
            (void)compress_log_output(((uint32_t)(lvl) << 26) | ((uint32_t)(nargs) << 22),   \
                                      (t), (t), ##__VA_ARGS__);                              \
    } while (0)

#define PB_ERR(stream) ((stream).errmsg != NULL ? (stream).errmsg : none_text)

/* Zeroes the oneof members of the shared package in the order the generated
 * *_init_zero assignments do (members overlap in the union). */
void dashboard_package_reset_4fdd6e(g2_dashboard_package_t *pkg)
{
    uint8_t *p = (uint8_t *)pkg;

    if (pkg == NULL)
        return;
    P8(p, 0x00) = 0;
    P32(p, 0x04) = 0;
    P16(p, 0x08) = 0;
    P32(p, 0x10) = 0;
    P8(p, 0x14) = 0;
    P32(p, 0x10) = 0;
    P16(p, 0x14) = 0;
    P32(p, 0x18) = 0;
    P32(p, 0x1c) = 0;
    P32(p, 0x2c) = 0;
    P16(p, 0x20) = 0;
    P16(p, 0x30) = 0;
    P16(p, 0x18) = 0;
    P32(p, 0x18) = 0;
    P8(p, 0x20) = 0;
    P32(p, 0x28) = 0;
    P8(p, 0x2c) = 0;
    P8(p, 0x2d) = 0;
    P64(p, 0x30) = 0;
    P16(p, 0x20) = 0;
    P32(p, 0x28) = 0;
    P32(p, 0x2c) = 0;
    P8(p, 0x30) = 0;
    P32(p, 0x38) = 0;
    P64(p, 0xc0) = 0;
    aeabi_memset_43c0e4(p + 0x3c, 0x80u, 0);
    aeabi_memset_43c0e4(p + 0xc8, 0x80u, 0);
    aeabi_memset_43c0e4(p + 0x148, 3000u, 0);
    P32(p, 0x28) = 0;
    P32(p, 0x2c) = 0;
    P8(p, 0x30) = 0;
    P64(p, 0xb8) = 0;
    P32(p, 0xc0) = 0;
    P32(p, 0xc4) = 0;
    P32(p, 0x148) = 0;
    P32(p, 0x14c) = 0;
    P32(p, 0x150) = 0;
    P64(p, 0x158) = 0;
    P64(p, 0x160) = 0;
    P32(p, 0x168) = 0;
    P32(p, 0x16c) = 0;
    P32(p, 0x170) = 0;
    P32(p, 0x174) = 0;
    P16(p, 0x178) = 0;
    aeabi_memset_43c0e4(p + 0x38, 0x40u, 0);
    aeabi_memset_43c0e4(p + 0x78, 0x40u, 0);
    aeabi_memset_43c0e4(p + 0xc8, 0x80u, 0);
    aeabi_memset_43c0e4(p + 0x17c, 0x2e4u, 0);
    P32(p, 0x28) = 0;
    P32(p, 0x2c) = 0;
    P8(p, 0x30) = 0;
    P32(p, 0x34) = 0;
    aeabi_memset_43c0e4(p + 0x38, 0xb0u, 0);
    aeabi_memset_43c0e4(p + 0xe8, 0x11bu, 0);
    aeabi_memset_43c0e4(p + 0x203, 0x40u, 0);
    P32(p, 0x10) = 0;
    P8(p, 0x14) = 0;
    P32(p, 0x10) = 0;
    P8(p, 0x14) = 0;
    P16(p, 0x16) = 0;
}

/* Encodes the shared package into the TX buffer and notifies the app; 0 on
 * encode failure (logged at `line`), else the BLE notify result. */
static uint32_t dashboard_notify_package(const char *fn, uint32_t line)
{
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_dashboard_tx_buffer, PB_TX_SIZE);

    if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package)) {
        DP_LOG(1u, fn, line, 1u, m_news_encode, t_news_encode, PB_ERR(stream));
        return 0u;
    }
    return Thread_MsgPbNotifyByBle(1u, 1u, g2_dashboard_tx_buffer, (uint16_t)stream.bytes_written);
}

uint32_t requesetAppUpgradeNewsInfo_4fe0aa(void)
{
    DP_LOG(3u, fn_upgrade, 0x1b4u, 0u, m_upgrade, t_upgrade);
    aeabi_memset_43c0e4(g2_dashboard_tx_buffer, PB_TX_SIZE, 0);
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 0x0bu;
    g2_dashboard_package.magic_random = 1u;
    g2_dashboard_package.which_payload = 0x0du;
    PKG_FIELD32(0x10) = 1u;
    return dashboard_notify_package(fn_upgrade, 0x1beu);
}

/* The stock trace reuses the "requesetAppUpgradeNewsInfo to app" text. */
uint32_t notifyAppNewsStatus_4fe1b4(uint8_t status, uint32_t index)
{
    DP_LOG(3u, fn_status, 0x1cdu, 0u, m_upgrade, t_upgrade);
    aeabi_memset_43c0e4(g2_dashboard_tx_buffer, PB_TX_SIZE, 0);
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 0x0cu;
    g2_dashboard_package.magic_random = 1u;
    g2_dashboard_package.which_payload = 0x0eu;
    PKG_FIELD8(0x10) = status;
    PKG_FIELD32(0x14) = index;
    return dashboard_notify_package(fn_status, 0x1d8u);
}

/* Encodes the shared package into the TX buffer and sends it as a response;
 * false on encode failure. */
static bool dashboard_tx_package(void)
{
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_dashboard_tx_buffer, PB_TX_SIZE);

    if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package))
        return false;
    (void)Thread_MsgPbTxByBle(1u, 1u, g2_dashboard_tx_buffer, (uint16_t)stream.bytes_written);
    return true;
}

static void dashboard_master_event(uint8_t event, bool delay)
{
    uint8_t msg[5];

    aeabi_memset_43c0e4(msg, sizeof msg, 0);
    msg[0] = event;
    if (delay)
        audio_uart_task_delay(50u);
    (void)audio_sync_send_to_both_ext_464f76(1u, msg, 1u, 0u, 5u);
}

/* which 0x0b: stores one news session record and answers with its status
 * (0 stored or no-news, 1 index out of range). */
static uint8_t dashboard_parse_send_news(void)
{
    uint8_t *sub = &g2_dashboard_package.payload[0];
    g2_news_session_t *table = (g2_news_session_t *)(void *)g2_news_staging_203024a4;
    uint32_t status = 0u;
    uint32_t session_id = P32(sub, 0x00);
    uint32_t field_08 = P32(sub, 0x08);
    uint32_t news_index = P32(sub, 0x0c);
    uint32_t news_id = P32(sub, 0x10);
    uint32_t idx, ret;
    uint8_t msg[5];
    bool all_valid;

    if (P32(sub, 0x04) == 1u) {
        DP_LOG(3u, fn_parse, 0x279u, 0u, m_no_news, t_no_news);
        if (audio_uart_service_mode() == 1u) {
            DP_LOG(3u, fn_parse, 0x27bu, 0u, m_master, t_master);
            if (audio_log_wake_allowed() == 1u && audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
                aeabi_memset_43c0e4(msg, sizeof msg, 0);
                msg[0] = 0x0du;
                (void)audio_uart_master_display_refresh(1u, msg, 1u, 0u);
            }
        }
    } else if (P32(sub, 0x0c) >= NEWS_SESSION_MAX) {
        DP_LOG(1u, fn_parse, 0x288u, 2u, m_range, t_range, P32(sub, 0x0c), 4u);
        status = 1u;
    } else if ((idx = P32(sub, 0x0c)) >= NEWS_SESSION_MAX) {
        DP_LOG(1u, fn_parse, 0x28eu, 2u, m_range, t_range, P32(sub, 0x0c), 4u);
        status = 1u;
    } else {
        (void)osMutexAcquire(g2_dashboard_mutex_200743a8, WAIT_FOREVER);
        if (table[0].session_id != P32(sub, 0x00) || P32(sub, 0x0c) == 0u)
            aeabi_memset_43c0e4(table, sizeof(g2_news_session_t) * NEWS_SESSION_MAX, 0);
        table[idx].valid = 1u;
        table[idx].session_id = P32(sub, 0x00);
        table[idx].field_08 = P32(sub, 0x08);
        table[idx].news_index = P32(sub, 0x0c);
        table[idx].news_id = P32(sub, 0x10);
        table[idx].stamp[0] = P32(sub, 0x98);
        table[idx].stamp[1] = P32(sub, 0x9c);
        (void)audio_settings_copy_text(table[idx].text_94, sub + 0x14, 0x7fu);
        table[idx].text_94[0x7f] = '\0';
        (void)audio_settings_copy_text(table[idx].text_14, sub + 0xa0, 0x7fu);
        table[idx].text_14[0x7f] = '\0';
        (void)audio_settings_copy_text(table[idx].body, sub + 0x120, 0x1b89u);
        table[idx].body[0x1b89] = '\0';
        (void)osMutexRelease(g2_dashboard_mutex_200743a8);

        all_valid = true;
        for (int32_t i = 0; i < (int32_t)NEWS_SESSION_MAX; i++) {
            if (table[i].valid != 1u) {
                all_valid = false;
                break;
            }
        }
        if (all_valid && audio_uart_service_mode() == 1u) {
            DP_LOG(3u, fn_parse, 0x2b3u, 0u, m_master, t_master);
            dashboard_master_event(0x10u, true);
        }
    }

    aeabi_memset_43c0e4(g2_dashboard_tx_buffer, PB_TX_SIZE, 0);
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 0x0au;
    g2_dashboard_package.magic_random = g2_dashboard_last_magic;
    PKG_FIELD8(0x08) = 0x0cu;
    PKG_FIELD8(0x09) = 0u;
    PKG_FIELD32(0x10) = session_id;
    PKG_FIELD32(0x14) = field_08;
    PKG_FIELD32(0x18) = news_index;
    PKG_FIELD32(0x1c) = news_id;
    PKG_FIELD32(0x20) = status;
    {
        g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_dashboard_tx_buffer, PB_TX_SIZE);

        if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package)) {
            DP_LOG(1u, fn_parse, 0x2ceu, 1u, m_news_encode, t_news_encode, PB_ERR(stream));
            return 0u;
        }
        ret = Thread_MsgPbTxByBle(1u, 1u, g2_dashboard_tx_buffer, (uint16_t)stream.bytes_written);
    }
    DP_LOG(3u, fn_parse, 0x2d4u, 2u, m_news_sent, t_news_sent, status, ret);
    return 1u;
}

/* which 4: display settings (inner 2), weather / widget data (inner 3), or a
 * word stored at +0x14ac (inner 4). */
static void dashboard_parse_settings(uint8_t *parsed)
{
    uint16_t inner;

    g2_dashboard_payload_ptr = &g2_dashboard_package.payload[0];
    g2_dashboard_settings_id = P32(g2_dashboard_payload_ptr, 0);
    inner = P16(g2_dashboard_payload_ptr, 4);
    if (inner == 2u) {
        g2_dashboard_settings_src = g2_dashboard_payload_ptr + 8;
        g2_dashboard_settings_dst = parsed + PARSED_SETTINGS;
        P32(g2_dashboard_settings_dst, 0x00) = P32(g2_dashboard_settings_src, 0x00);
        P32(g2_dashboard_settings_dst, 0x04) = P32(g2_dashboard_settings_src, 0x04);
        P32(g2_dashboard_settings_dst, 0x14) = P32(g2_dashboard_settings_src, 0x14);
        P32(g2_dashboard_settings_dst, 0x24) = P32(g2_dashboard_settings_src, 0x24);
        P32(g2_dashboard_settings_dst, 0x28) = P32(g2_dashboard_settings_src, 0x28);
        /* pb bytes fields {u16 size, bytes[]} at +0x08 and +0x18 */
        (void)audio_queue_copy_bytes(g2_dashboard_settings_dst + 0x08, g2_dashboard_settings_src + 0x0a,
                                     P16(g2_dashboard_settings_src, 0x08));
        (void)audio_queue_copy_bytes(g2_dashboard_settings_dst + 0x18, g2_dashboard_settings_src + 0x1a,
                                     P16(g2_dashboard_settings_src, 0x18));
        P8(parsed, PARSED_HAS_SETTINGS) = 1u;
    } else if (inner > 1u) {
        if (inner == 4u) {
            g2_dashboard_word_ptr = g2_dashboard_payload_ptr + 8;
            P32(parsed, PARSED_WORD_14AC) = P32(g2_dashboard_word_ptr, 0);
            P8(parsed, PARSED_HAS_14AC) = 1u;
        } else if (inner < 4u) {
            g2_dashboard_widget_ptr = g2_dashboard_payload_ptr + 8;
            if (P16(g2_dashboard_widget_ptr, 0) == 1u) {
                g2_dashboard_weather_ptr = g2_dashboard_widget_ptr + 8;
                (void)dashboard_parse_weather_4fda24(g2_dashboard_weather_ptr, parsed);
            } else if (P16(g2_dashboard_widget_ptr, 0) == 2u) {
                g2_dashboard_widget_data_ptr = g2_dashboard_widget_ptr + 8;
                (void)dashboard_parse_widget_data_4fdad4(g2_dashboard_widget_data_ptr, parsed);
            }
        }
    }
}

/* Decodes one phone package into `parsed` (0x14c0 bytes, see
 * dashboard_async_update_data) and answers the news / clear-all requests
 * directly. 1 = handled, 0 = error. */
uint8_t dashboard_parse_data_package_4fe318(const uint8_t *data, uint32_t length, uint8_t *parsed)
{
    g2_pb_istream_t in;
    int32_t count;

    if (data == NULL || parsed == NULL) {
        DP_LOG(1u, fn_parse, 0x1eeu, 2u, m_bad_param, t_bad_param, data, parsed);
        return 0u;
    }
    dashboard_parsed_data_reset_4fd93c(parsed);
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    in = pb_istream_from_buffer(data, length);
    if (!pb_decode(&in, g2_dashboard_package_fields, &g2_dashboard_package)) {
        DP_LOG(1u, fn_parse, 0x1fcu, 1u, m_decode, t_decode, PB_ERR(in));
        return 0u;
    }
    g2_dashboard_last_command_id = g2_dashboard_package.command_id;
    g2_dashboard_last_magic = g2_dashboard_package.magic_random;

    switch (g2_dashboard_package.which_payload) {
    case 4u:
        dashboard_parse_settings(parsed);
        break;
    case 7u:
        if (PKG_FIELD32(0x10) == 1u)
            P8(parsed, PARSED_REQ_NEWS) = 1u;
        break;
    case 9u: {
        g2_news_session_t *table = (g2_news_session_t *)(void *)g2_news_staging_203024a4;

        if (g2_dashboard_last_command_id != 7u) {
            DP_LOG(1u, fn_parse, 0x238u, 0u, m_news_cmd, t_news_cmd);
            return 0u;
        }
        P8(parsed, PARSED_NEWS_V2) = 1u;
        count = 0;
        aeabi_memset_43c0e4(g2_dashboard_tx_buffer, PB_TX_SIZE, 0);
        dashboard_package_reset_4fdd6e(&g2_dashboard_package);
        g2_dashboard_package.command_id = 8u;
        g2_dashboard_package.magic_random = g2_dashboard_last_magic;
        PKG_FIELD8(0x08) = 0x0au;
        PKG_FIELD8(0x09) = 0u;
        for (int32_t i = 0; i < (int32_t)NEWS_SESSION_MAX; i++) {
            if (table[i].valid == 1u) {
                PKG_FIELD32(0x18 + 4 * i) = table[i].news_id;  /* slot i, not slot count */
                count++;
            }
        }
        PKG_FIELD16(0x14) = (uint16_t)count;
        PKG_FIELD32(0x10) = (uint32_t)count;
        if (!dashboard_tx_package())
            return 0u;
        break;
    }
    case 0x0bu:
        if (g2_dashboard_last_command_id != 9u) {
            DP_LOG(1u, fn_parse, 0x264u, 2u, m_send_cmd, t_send_cmd, 9u, g2_dashboard_last_command_id);
            return 0u;
        }
        P8(parsed, PARSED_NEWS_V2) = 1u;
        return dashboard_parse_send_news();
    case 0x0fu:
        if (g2_dashboard_last_command_id != 0x0du) {
            DP_LOG(1u, fn_parse, 0x214u, 0u, m_clear_cmd, t_clear_cmd);
            return 0u;
        }
        P8(parsed, PARSED_NEWS_V2) = 1u;
        aeabi_memset_43c0e4(g2_dashboard_tx_buffer, PB_TX_SIZE, 0);
        dashboard_package_reset_4fdd6e(&g2_dashboard_package);
        g2_dashboard_package.command_id = 0x0eu;
        g2_dashboard_package.magic_random = g2_dashboard_last_magic;
        PKG_FIELD8(0x08) = 0x10u;
        PKG_FIELD8(0x09) = 0u;
        PKG_FIELD8(0x10) = 1u;
        PKG_FIELD8(0x11) = 0u;
        PKG_FIELD8(0x12) = 0u;
        PKG_FIELD8(0x13) = 0u;
        if (!dashboard_tx_package())
            return 0u;
        if (audio_uart_service_mode() == 1u)
            dashboard_master_event(0x11u, false);
        break;
    default:
        DP_LOG(3u, fn_parse, 0x335u, 1u, m_unsupported, t_unsupported,
               (uint32_t)g2_dashboard_package.which_payload);
        return 0u;
    }
    return 1u;
}

/* Encodes the which-3 response {settings id, result} into buf; *len is the
 * buffer size on entry and the encoded size on success. 1 ok, 0 failed. */
uint32_t dashboard_respond_encode_4fec14(uint8_t result, uint8_t *buf, uint32_t *len)
{
    g2_pb_ostream_t stream;

    if (buf == NULL || len == NULL || *len == 0u)
        return 0u;
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 1u;
    g2_dashboard_package.magic_random = g2_dashboard_last_magic;
    g2_dashboard_package.which_payload = 3u;
    PKG_FIELD32(0x10) = g2_dashboard_settings_id;
    PKG_FIELD8(0x14) = result;
    stream = pb_ostream_from_buffer(buf, *len);
    if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package))
        return 0u;
    *len = stream.bytes_written;
    return 1u;
}

/* Answers the last request: result 0 for ret 0, 2 for ret 2 (deprecated
 * legacy news), else 1. Returns 1 no request, 2 encode failure, or the BLE
 * TX result. */
uint32_t dashboard_respond_to_app_serialize_4fec98(uint32_t ret)
{
    uint32_t len = PB_TX_SIZE;
    uint8_t buf[PB_TX_SIZE];
    uint8_t result;
    uint32_t tx;

    if (g2_dashboard_last_command_id == 0u) {
        DP_LOG(2u, fn_respond, 0x367u, 0u, m_cmd_invalid, t_cmd_invalid);
        return 1u;
    }
    aeabi_memset_43c0e4(buf, sizeof buf, 0);
    result = (uint8_t)(ret != 0u);
    if (ret == 2u) {
        DP_LOG(3u, fn_respond, 0x373u, 0u, m_deprecated, t_deprecated);
        result = 2u;
    }
    if (dashboard_respond_encode_4fec14(result, buf, &len) == 0u) {
        DP_LOG(1u, fn_respond, 0x37cu, 0u, m_respond_failed, t_respond_failed);
        return 2u;
    }
    tx = Thread_MsgPbTxByBle(1u, 1u, buf, (uint16_t)len);
    if (tx == 0u) {
        aeabi_memset_43c0e4(buf, PB_TX_SIZE, 0);
        tx = 0u;
    }
    return tx;
}

/* which-8 reply to a news info request; returns 1 no request, 0 encode
 * failure or sent, else the BLE TX error. */
uint32_t dashboard_respond_NewsInfo_to_app_4fedcc(uint32_t ret)
{
    uint8_t buf[PB_TX_SIZE];
    g2_pb_ostream_t stream;
    uint32_t tx;

    if (g2_dashboard_last_command_id == 0u) {
        DP_LOG(2u, fn_newsinfo, 0x398u, 0u, m_cmd_invalid, t_cmd_invalid);
        return 1u;
    }
    aeabi_memset_43c0e4(buf, sizeof buf, 0);
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 6u;
    g2_dashboard_package.magic_random = g2_dashboard_last_magic;
    g2_dashboard_package.which_payload = 8u;
    if (ret == 2u)
        DP_LOG(3u, fn_newsinfo, 0x3a5u, 0u, m_deprecated, t_deprecated);
    PKG_FIELD32(0x10) = 0x55aau;
    stream = pb_ostream_from_buffer(buf, PB_TX_SIZE);
    if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package))
        return 0u;
    tx = Thread_MsgPbTxByBle(1u, 1u, buf, (uint16_t)stream.bytes_written);
    if (tx == 0u) {
        aeabi_memset_43c0e4(buf, PB_TX_SIZE, 0);
        tx = 0u;
    }
    return tx;
}

/* Encodes a which-6 / command-3 message (magic 0x12345678) from `msg`.
 * data_type 1: notification status {count, optional two floats when either
 * is >= 0}; 2: widget state (sub type at +8: 1 two-mode values, 2 text,
 * 3 two words); 3: 64 raw bytes. 1 ok (*len updated), 0 failed. */
uint32_t dashboard_send_to_app_serialize_internal_4fef04(const g2_dashboard_app_msg_t *msg,
                                                         uint8_t *buf, uint32_t *len)
{
    const uint8_t *m = (const uint8_t *)msg;
    g2_pb_ostream_t stream;
    uint8_t sub;

    if (msg == NULL || buf == NULL || len == NULL || *len == 0u)
        return 0u;
    dashboard_package_reset_4fdd6e(&g2_dashboard_package);
    g2_dashboard_package.command_id = 3u;
    g2_dashboard_package.magic_random = 0x12345678u;
    g2_dashboard_package.which_payload = 6u;
    PKG_FIELD32(0x10) = msg->package_id;
    PKG_FIELD8(0x14) = msg->flag;
    switch (msg->data_type) {
    case 1u:
        PKG_FIELD16(0x16) = 3u;
        PKG_FIELD8(0x18) = 1u;
        PKG_FIELD32(0x1c) = P32(m, 0x08);
        if (PF(m, 0x0c) >= 0.0f || PF(m, 0x10) >= 0.0f) {
            PKG_FIELD8(0x20) = 1u;
            PKG_FIELD32(0x24) = P32(m, 0x0c);
            PKG_FIELD32(0x28) = P32(m, 0x10);
        }
        break;
    case 2u:
        sub = P8(m, 0x08);
        if (sub == 1u) {
            PKG_FIELD16(0x16) = 4u;
            PKG_FIELD16(0x18) = 1u;
            if (P8(m, 0x10) == 1u) {
                PKG_FIELD16(0x20) = 1u;
                PKG_FIELD32(0x28) = P32(m, 0x18);
                PKG_FIELD32(0x2c) = P32(m, 0x1c);
            } else if (P8(m, 0x10) == 2u) {
                PKG_FIELD16(0x20) = 2u;
                PKG_FIELD32(0x28) = P32(m, 0x18);
                PKG_FIELD32(0x30) = P32(m, 0x20);
                PKG_FIELD32(0x34) = P32(m, 0x24);
            }
        } else if (sub == 2u) {
            PKG_FIELD16(0x16) = 4u;
            PKG_FIELD16(0x18) = 2u;
            (void)audio_settings_copy_text(&g2_dashboard_package.payload[0x20 - 0x10], m + 0x10, 0x3fu);
        } else if (sub == 3u) {
            PKG_FIELD16(0x16) = 4u;
            PKG_FIELD16(0x18) = 3u;
            PKG_FIELD32(0x20) = P32(m, 0x10);
            PKG_FIELD32(0x24) = P32(m, 0x14);
        }
        break;
    case 3u:
        PKG_FIELD16(0x16) = 5u;
        (void)audio_uart_display_area_copy_439c04(&g2_dashboard_package.payload[0x18 - 0x10], m + 0x08,
                                                  0x40u);
        break;
    default:
        break;
    }
    stream = pb_ostream_from_buffer(buf, *len);
    if (!pb_encode(&stream, g2_dashboard_package_fields, &g2_dashboard_package)) {
        DP_LOG(1u, fn_send_internal, 0x43bu, 0u, m_send_encode, t_send_encode);
        return 0u;
    }
    *len = stream.bytes_written;
    return 1u;
}

/* Returns 1 NULL message, 2 encode failure, else the BLE notify result. */
uint32_t dashboard_send_to_app_serialize_4ff09c(const g2_dashboard_app_msg_t *msg)
{
    uint32_t len = 0x200u;
    uint8_t buf[0x200];
    uint32_t ret;

    if (msg == NULL) {
        DP_LOG(1u, fn_send, 0x44fu, 0u, m_send_null, t_send_null);
        return 1u;
    }
    aeabi_memset_43c0e4(buf, sizeof buf, 0);
    if (dashboard_send_to_app_serialize_internal_4fef04(msg, buf, &len) == 0u) {
        DP_LOG(1u, fn_send, 0x458u, 0u, m_send_encode, t_send_encode);
        return 2u;
    }
    ret = Thread_MsgPbNotifyByBle(1u, 1u, buf, (uint16_t)len);
    if (ret == 0u)
        return 0u;
    DP_LOG(1u, fn_send, 0x460u, 1u, m_ble_fail, t_ble_fail, ret);
    return ret;
}
