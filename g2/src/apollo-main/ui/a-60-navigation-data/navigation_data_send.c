/* Navigation glasses-to-phone senders, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_data_handler.c
 * (ROM 0x6e8b84). Native 0x586448..0x587185 (16 senders; literal pools
 * 0x586f04..0x586f13 and 0x58704c..0x58705b sit between them).
 *
 * Every sender fills one 0x2024-byte navigation message, nanopb-encodes it
 * (fields descriptor ROM 0x7798a4) into a 10000-byte buffer and hands the
 * encoded bytes to the BLE protobuf transport with service id 1, command 8.
 * The "allocating" senders take both buffers from the file heap and use the
 * notify path (0x475c1a); the "shared" senders reuse the static message
 * (RAM 0x20358dd4) and buffer (RAM 0x20350430) and use the tx path (0x475b14).
 * All allocating senders log the stock copy-pasted "request_location_list"
 * malloc messages; only the function name and line number differ. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define NAV_MSG_SIZE 0x2024u
#define NAV_TX_BUF_SIZE 10000u
#define NAV_BLE_SERVICE 1u
#define NAV_BLE_COMMAND 8u

/* nanopb 0.4 pb_ostream_t. */
typedef struct {
    void *callback;         /* +0x00 */
    void *state;            /* +0x04 */
    uint32_t max_size;      /* +0x08 */
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;     /* +0x10 */
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_ostream_t) == 0x14, "pb_ostream_t is 20 bytes");

/* Navigation message (nanopb struct). `which` selects the payload member. */
typedef struct {
    uint8_t type;   /* +0x0 message type id (0..17) */
    uint8_t input;  /* +0x1 caller argument / sequence */
    uint16_t which; /* +0x2 oneof tag */
    union {
        uint8_t value;      /* which 3: +0x4 */
        uint32_t value32;   /* which 9 / 10: +0x4 */
        struct {
            uint8_t reserved[0x188];
            uint8_t value;  /* +0x18c */
        } w5;
        struct {
            uint32_t a;                /* +0x0004 */
            uint32_t b;                /* +0x0008 */
            uint8_t reserved0[0x2002];
            uint8_t flag;              /* +0x200e */
            uint8_t reserved1[9];
            uint32_t c;                /* +0x2018 */
            uint32_t d;                /* +0x201c */
            uint32_t e;                /* +0x2020 */
        } w6;
        struct {
            char name[0x44];          /* +0x04 location name, not terminated by the copy */
            uint32_t location_index;  /* +0x48 */
            uint32_t mode;            /* +0x4c */
        } w8;
    } u;
} g2_nav_msg_t;
_Static_assert(sizeof(g2_nav_msg_t) == NAV_MSG_SIZE, "navigation message is 0x2024 bytes");
_Static_assert(offsetof(g2_nav_msg_t, u.w5.value) == 0x18c, "which 5 byte");
_Static_assert(offsetof(g2_nav_msg_t, u.w6.flag) == 0x200e, "which 6 flag");
_Static_assert(offsetof(g2_nav_msg_t, u.w6.c) == 0x2018, "which 6 c");
_Static_assert(offsetof(g2_nav_msg_t, u.w8.location_index) == 0x48, "which 8 index");

extern g2_nav_msg_t g2_nav_msg_shared_20358dd4;             /* RAM 0x20358dd4 */
extern uint8_t g2_nav_tx_buf_20350430[NAV_TX_BUF_SIZE];     /* RAM 0x20350430 */
extern const uint8_t g2_nav_msg_fields_7798a4[];            /* ROM 0x7798a4 nanopb descriptor */

extern void *file_heap_allocate(uint32_t size);             /* 0x474cd2 */
extern void file_heap_free(void *ptr);                      /* 0x474d16 */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len); /* 0x439be4 memcpy */
extern g2_pb_ostream_t pb_ostream_from_buffer(uint8_t *buf, size_t bufsize); /* 0x4905f4 */
extern bool pb_encode(g2_pb_ostream_t *stream, const void *fields, const void *src); /* 0x490c32 */
/* 0x475b14 Thread_MsgPbTxByBle / 0x475c1a Thread_MsgPbNotifyByBle (TSV names). */
extern uint32_t Thread_MsgPbTxByBle(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t Thread_MsgPbNotifyByBle(uint32_t, uint32_t, const void *, uint32_t);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

int32_t navigation_send_type_1_allocating(void);
int32_t navigation_send_type_13_allocating(void);
int32_t navigation_send_type_17_allocating(void);
int32_t navigation_send_type_16_allocating(void);
int32_t navigation_send_type_0_shared(uint8_t input);
int32_t navigation_send_type_5_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_6_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_10_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_11_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_12_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_7_shared(uint8_t input, uint8_t value);
int32_t navigation_send_type_8_shared(uint8_t input, uint8_t flag, uint32_t c, uint32_t a,
                                      uint32_t b, uint32_t d, uint32_t e);
int32_t navigation_send_type_4_allocating(uint8_t input, const char *name, uint32_t name_len,
                                          uint32_t location_index, uint32_t mode);
int32_t navigation_send_type_14_allocating(uint32_t view);
int32_t navigation_send_type_15_allocating(uint32_t heading);

static const char module_tag[] = "navigation.datahandler"; /* ROM 0x7798bc */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_data_handler.c"; /* ROM 0x6e8b84 */
static const char msg_alloc_failed[] =
    "navigation_ui_request_location_list: malloc failed for nav_msg_ptr"; /* ROM 0x703ca8 */
static const char msg_alloc_failed_short[] =
    "[navigation.datahandler]navigation_ui_request_location_list: malloc failed for nav_msg_ptr"; /* ROM 0x6e0bec */
static const char buf_alloc_failed[] =
    "navigation_ui_request_location_list: malloc failed for resp_buf_ptr"; /* ROM 0x703cec */
static const char buf_alloc_failed_short[] =
    "[navigation.datahandler]navigation_ui_request_location_list: malloc failed for resp_buf_ptr"; /* ROM 0x6e0c48 */
static const char fn_location_list[] = "navigation_ui_notify_location_list";             /* ROM 0x756c6c */
static const char fn_exit[] = "navigation_ui_notify_exit";                               /* ROM 0x76e6c4 */
static const char fn_calib_complete[] = "navigation_ui_notify_compass_calibration_complete"; /* ROM 0x72ae88 */
static const char fn_calib_start[] = "navigation_ui_notify_compass_calibration_start";   /* ROM 0x7358c4 */
static const char fn_select_index[] = "navigation_notify_location_select_index_cmd";     /* ROM 0x740290 */
static const char fn_view_changed[] = "navigation_notify_view_changed_cmd";              /* ROM 0x756c90 */
static const char fn_compass_changed[] = "navigation_notify_compass_changed_cmd";        /* ROM 0x74b554 */
static const char select_index_fmt[] =
    "navigation_notify_location_select_index_cmd: location_name=%s, location_index=%d, mode_index=%d"; /* ROM 0x6ddd74 */
static const char select_index_fmt_short[] =
    "[navigation.datahandler]navigation_notify_location_select_index_cmd: location_name=%s, location_index=%d, mode_index=%d"; /* ROM 0x6d65d8 */

/* ---- allocating senders: heap message + heap buffer, notify path ---- */

int32_t navigation_send_type_1_allocating(void)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_location_list, 0x4cu, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_location_list, 0x53u, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 1u;
    msg->input = 0u;
    msg->which = 3u;
    msg->u.value = 0u;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

int32_t navigation_send_type_13_allocating(void)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_exit, 0x80u, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_exit, 0x87u, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 13u;
    msg->input = 0u;
    msg->which = 3u;
    msg->u.value = 0u;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

int32_t navigation_send_type_17_allocating(void)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_calib_complete, 0xafu, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_calib_complete, 0xb6u, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 17u;
    msg->input = 0u;
    msg->which = 3u;
    msg->u.value = 0u;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

int32_t navigation_send_type_16_allocating(void)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_calib_start, 0xdfu, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_calib_start, 0xe6u, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 16u;
    msg->input = 0u;
    msg->which = 3u;
    msg->u.value = 0u;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

/* ---- shared senders: static message + static buffer, tx path ---- */

int32_t navigation_send_type_0_shared(uint8_t input)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 0u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = 0u;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

int32_t navigation_send_type_5_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 5u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

int32_t navigation_send_type_6_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 6u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

int32_t navigation_send_type_10_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 10u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

int32_t navigation_send_type_11_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 11u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

int32_t navigation_send_type_12_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 12u;
    msg->input = input;
    msg->which = 3u;
    msg->u.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

/* oneof tag 5: the byte lives at +0x18c. */
int32_t navigation_send_type_7_shared(uint8_t input, uint8_t value)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 7u;
    msg->input = input;
    msg->which = 5u;
    msg->u.w5.value = value;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

/* oneof tag 6. Argument order follows the stock register/stack order:
 * r0 input, r1 flag (+0x200e), r2 c (+0x2018), r3 a (+0x4), stack b (+0x8),
 * d (+0x201c), e (+0x2020). */
int32_t navigation_send_type_8_shared(uint8_t input, uint8_t flag, uint32_t c, uint32_t a,
                                      uint32_t b, uint32_t d, uint32_t e)
{
    g2_nav_msg_t *msg = &g2_nav_msg_shared_20358dd4;
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 8u;
    msg->input = input;
    msg->which = 6u;
    msg->u.w6.flag = flag;
    msg->u.w6.c = c;
    msg->u.w6.a = a;
    msg->u.w6.b = b;
    msg->u.w6.d = d;
    msg->u.w6.e = e;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg))
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, g2_nav_tx_buf_20350430,
                                                (uint16_t)stream.bytes_written);
}

/* oneof tag 8: selected location (name copied without terminator into the
 * zeroed message, index, mode). */
int32_t navigation_send_type_4_allocating(uint8_t input, const char *name, uint32_t name_len,
                                          uint32_t location_index, uint32_t mode)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_select_index, 0x1e7u, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_select_index, 0x1eeu, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, fn_select_index, 0x1f5u, select_index_fmt,
                           name, location_index, mode);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0cc00000u, select_index_fmt_short, select_index_fmt_short,
                                  name, location_index, mode);
    msg->type = 4u;
    msg->input = input;
    msg->which = 8u;
    msg->u.w8.location_index = location_index;
    msg->u.w8.mode = mode;
    audio_uart_checksum_copy(msg->u.w8.name, name, name_len);
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

/* oneof tag 9: view state (callers pass 2 = show, 1 = hide). */
int32_t navigation_send_type_14_allocating(uint32_t view)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_view_changed, 0x219u, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_view_changed, 0x220u, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 14u;
    msg->input = 0u;
    msg->which = 9u;
    msg->u.value32 = view;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}

/* oneof tag 10: compass heading word. */
int32_t navigation_send_type_15_allocating(uint32_t heading)
{
    g2_nav_msg_t *msg = file_heap_allocate(NAV_MSG_SIZE);
    if (msg == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_compass_changed, 0x248u, msg_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, msg_alloc_failed_short, msg_alloc_failed_short);
        return -1;
    }
    uint8_t *buf = file_heap_allocate(NAV_TX_BUF_SIZE);
    if (buf == NULL) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module_tag, source_file, fn_compass_changed, 0x24fu, buf_alloc_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compress_log_output(0x04000000u, buf_alloc_failed_short, buf_alloc_failed_short);
        file_heap_free(msg);
        return -1;
    }
    aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    aeabi_memset_43c0e4(buf, NAV_TX_BUF_SIZE, 0);
    msg->type = 15u;
    msg->input = 0u;
    msg->which = 10u;
    msg->u.value32 = heading;
    g2_pb_ostream_t stream = pb_ostream_from_buffer(buf, NAV_TX_BUF_SIZE);
    if (!pb_encode(&stream, g2_nav_msg_fields_7798a4, msg)) {
        file_heap_free(msg);
        file_heap_free(buf);
        return 0;
    }
    int32_t result = (int32_t)Thread_MsgPbNotifyByBle(NAV_BLE_SERVICE, NAV_BLE_COMMAND, buf,
                                                          (uint16_t)stream.bytes_written);
    file_heap_free(msg);
    file_heap_free(buf);
    return result;
}
