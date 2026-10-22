/* Product FreeRTOS-Plus-CLI "terminal" test module helpers, stock directory
 * D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\prvCommand\
 * (file name not retained). Native 0x5828f8..0x582abd, pool
 * 0x582ac0..0x582b0b and 0x5836b0..0x5836b7. The command handler that uses
 * them follows at 0x582b0c.
 *
 * Packages are encoded with the terminal TX nanopb descriptor (ROM
 * 0x77c634) and pushed to both arms as sync app 0x30. */
#include <stddef.h>
#include <stdint.h>
#include "cli_commands.h"

#define TERMINAL_SYNC_APP 0x30u
#define TERMINAL_PB_BYTES 0x878u
#define TERMINAL_SESSION_MAX 10u
#define TERMINAL_SESSION_NAME_BYTES 0x80u
#define TERMINAL_SESSION_SELECTED 1u
#define TERMINAL_SESSION_OTHER 3u

/* nanopb pb_ostream_t */
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "pb_ostream_t");

/* Length-prefixed byte field (pb bytes/string with a u16 size). */
typedef struct {
    uint16_t length; /* +0x0 */
    uint8_t data[];  /* +0x2 */
} g2_terminal_bytes_t;

typedef struct {
    uint32_t id;                                /* +0x00 1-based */
    uint16_t name_length;                       /* +0x04 */
    char name[TERMINAL_SESSION_NAME_BYTES];     /* +0x06 */
    uint8_t state;                              /* +0x86 1 selected, 3 other */
    uint8_t pad0;
} g2_terminal_session_t;
_Static_assert(sizeof(g2_terminal_session_t) == 0x88u, "session row");

typedef struct {
    int32_t host;                               /* +0x00 copied from the caller (its "host" value) */
    int32_t selected;                           /* +0x04 1-based id */
    uint16_t count;                             /* +0x08 */
    uint8_t pad0[2];
    g2_terminal_session_t sessions[TERMINAL_SESSION_MAX]; /* +0x0c */
} g2_terminal_session_list_t;
_Static_assert(sizeof(g2_terminal_session_list_t) == 0x55cu, "session list");

/* Package header: cmd, magic. */
typedef struct {
    uint8_t cmd;
    uint8_t magic;
} g2_terminal_pkg_header_t;

extern uint8_t g2_terminal_cli_pb_buffer_201011a4[TERMINAL_PB_BYTES];
extern const struct pb_msgdesc_candidate audio_terminal_tx_pb_descriptor; /* ROM 0x77c634 */

extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size); /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);       /* 0x490c32 */
extern uint32_t audio_sync_send_to_both_ext_464f76(uint32_t app, const void *bytes, uint32_t length,
                                                   uint32_t id, uint32_t event);
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* memcpy */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);            /* 0x439be4 memcpy */
extern uint32_t g2_log_module_length(const char *text);                       /* 0x44a43c strlen */
extern int32_t g2_audio_dump_snprintf(char *dst, uint32_t size, const char *format, ...); /* 0x44b728 */

static const char s_session_none[] = "SESSION_STATUS_NONE";             /* ROM 0x782920 */
static const char s_session_thinking[] = "SESSION_STATUS_THINKING";     /* ROM 0x77ac0c */
static const char s_session_await[] = "SESSION_STATUS_AWAIT_USER";      /* ROM 0x770318 */
static const char s_session_done[] = "SESSION_STATUS_DONE";             /* ROM 0x782934 */
static const char s_session_reset[] = "SESSION_STATUS_RESET";           /* ROM 0x77ac24 */
static const char s_session_unknown[] = "SESSION_STATUS_UNKNOWN";       /* ROM 0x77ac3c */
static const char s_style_highlight[] = "STYLE_HIGHLIGHT";              /* ROM 0x788260 */
static const char s_style_dim[] = "STYLE_DIM";                          /* ROM 0x78baf8 */
static const char s_style_user[] = "STYLE_USER";                        /* ROM 0x78bb04 */
static const char s_style_unknown[] = "STYLE_UNKNOWN";                  /* ROM 0x788270 */
static const char s_host_none[] = "HOST_STATUS_NO_HOST";                /* ROM 0x782948 */
static const char s_host_offline[] = "HOST_STATUS_OFFLINE";             /* ROM 0x78295c */
static const char s_host_streaming[] = "HOST_STATUS_STREAMING";         /* ROM 0x77ac54 */
static const char s_host_unknown[] = "HOST_STATUS_UNKNOWN";             /* ROM 0x782970 */
static const char s_pkg_null[] = "terminal cli: pkg is NULL\r\n";       /* ROM 0x770334 */
static const char s_encode_failed[] = "terminal cli: pb encode failed\r\n"; /* ROM 0x758964 */
static const char s_send_failed[] = "terminal cli: send failed, ret=%d\r\n"; /* ROM 0x758988 */
static const char s_sent[] = "terminal cli: sent cmd=%d, magic=%d, len=%d\r\n"; /* ROM 0x737124 */
static const char s_session_name[] = "Session %lu";                     /* ROM 0x78bb10 */

const char *terminal_session_status_name_5828f8(uint8_t status);
const char *terminal_style_name_582924(uint8_t style);
const char *terminal_host_status_name_582942(uint8_t status);
int32_t terminal_cli_send_582960(const g2_terminal_pkg_header_t *pkg);
void terminal_text_copy_5829e0(g2_terminal_bytes_t *field, uint32_t capacity,
                                   const void *source, int32_t length);
void terminal_text_copy_string_582a1a(g2_terminal_bytes_t *field, uint32_t capacity, const char *text);
void terminal_session_list_fill_582a48(g2_terminal_session_list_t *list, int32_t host,
                                       int32_t selected, uint32_t count);

const char *terminal_session_status_name_5828f8(uint8_t status)
{
    switch (status) {
    case 0u: return s_session_none;
    case 1u: return s_session_thinking;
    case 2u: return s_session_await;
    case 3u: return s_session_done;
    case 4u: return s_session_reset;
    default: return s_session_unknown;
    }
}

const char *terminal_style_name_582924(uint8_t style)
{
    switch (style) {
    case 0u: return s_style_highlight;
    case 1u: return s_style_dim;
    case 2u: return s_style_user;
    default: return s_style_unknown;
    }
}

const char *terminal_host_status_name_582942(uint8_t status)
{
    switch (status) {
    case 0u: return s_host_none;
    case 1u: return s_host_offline;
    case 2u: return s_host_streaming;
    default: return s_host_unknown;
    }
}

int32_t terminal_cli_send_582960(const g2_terminal_pkg_header_t *pkg)
{
    g2_pb_ostream_t created;
    g2_pb_ostream_t stream;
    uint32_t status;

    if (pkg == NULL) {
        audio_ble_hci_boot_log_4733ee(s_pkg_null);
        return -1;
    }
    audio_pb_ostream_from_buffer(&created, g2_terminal_cli_pb_buffer_201011a4, TERMINAL_PB_BYTES);
    (void)audio_uart_display_area_copy_439c04(&stream, &created, sizeof(stream));
    if (audio_pb_encode(&stream, &audio_terminal_tx_pb_descriptor, pkg) == 0u) {
        audio_ble_hci_boot_log_4733ee(s_encode_failed);
        return -1;
    }
    status = audio_sync_send_to_both_ext_464f76(TERMINAL_SYNC_APP, g2_terminal_cli_pb_buffer_201011a4,
                                                (uint16_t)stream.bytes_written, 0u, 0u);
    if (status != 0u) {
        audio_ble_hci_boot_log_4733ee(s_send_failed, status);
        return -1;
    }
    audio_ble_hci_boot_log_4733ee(s_sent, pkg->cmd, pkg->magic, stream.bytes_written);
    return 0;
}

/* Copy at most capacity bytes; a NULL or empty source clears the field. */
void terminal_text_copy_5829e0(g2_terminal_bytes_t *field, uint32_t capacity,
                                   const void *source, int32_t length)
{
    uint32_t n;

    if (field == NULL || capacity == 0u)
        return;
    if (source == NULL || length < 1) {
        field->length = 0u;
        return;
    }
    n = (uint32_t)length;
    if (capacity < n)
        n = capacity;
    if (n != 0u)
        (void)audio_queue_copy_bytes(field->data, source, n);
    field->length = (uint16_t)n;
}

void terminal_text_copy_string_582a1a(g2_terminal_bytes_t *field, uint32_t capacity, const char *text)
{
    if (text == NULL)
        terminal_text_copy_5829e0(field, capacity, NULL, 0);
    else
        terminal_text_copy_5829e0(field, capacity, text, (int32_t)g2_log_module_length(text));
}

/* Fake session list "Session 1".."Session n" (n <= 10); the row whose id
 * equals selected is marked 1, the others 3. */
void terminal_session_list_fill_582a48(g2_terminal_session_list_t *list, int32_t host,
                                       int32_t selected, uint32_t count)
{
    char name[32];
    uint32_t i;

    if (list == NULL)
        return;
    if (count >= TERMINAL_SESSION_MAX + 1u)
        count = TERMINAL_SESSION_MAX;
    list->host = host;
    list->selected = selected;
    list->count = (uint16_t)count;
    for (i = 0u; i < count; i++) {
        g2_terminal_session_t *session = &list->sessions[i];

        session->id = i + 1u;
        session->state = (i + 1u == (uint32_t)selected) ? TERMINAL_SESSION_SELECTED : TERMINAL_SESSION_OTHER;
        if (g2_audio_dump_snprintf(name, sizeof(name), s_session_name, i + 1u) < 0)
            name[0] = '\0';
        terminal_text_copy_string_582a1a((g2_terminal_bytes_t *)&session->name_length,
                                         TERMINAL_SESSION_NAME_BYTES, name);
    }
}
