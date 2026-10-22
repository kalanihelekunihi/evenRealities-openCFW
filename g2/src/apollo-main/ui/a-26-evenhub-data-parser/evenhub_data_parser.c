/* EvenHub protobuf command dispatcher, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_data_parser.c (log tag
 * "evenhub.data_parser"). Native 0x4da834..0x4dbdcc (evenhub_data_parser); literal pools
 * 0x4db4b8..0x4db4d8, 0x4db5cc..0x4db5e0, 0x4db6a4..0x4db6b8, 0x4db7b8..0x4db7c0,
 * 0x4db83c..0x4db86c, 0x4dbc74..0x4dbc8c and 0x4dbdcc..0x4dbeac.
 *
 * Called from the EvenHub main task (0x4e11e6, return value ignored) with one raw protobuf
 * message from the phone app. The message is decoded into g2_evenhub_parser_msg and then
 * either forwarded to the EvenHub UI app (sync app id 0xe0) or answered directly.
 * Image raw-data fragments (cmd 3) are reassembled here straight into the target image
 * container's receive buffer. */
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>

#define EVENHUB_APP_ID 0xe0u
#define EVENHUB_LOADING_APP_ID 0xffeu
#define EVENHUB_START_RECORD_KEY 0x40101u
#define EVENHUB_MAX_OBJECTS 13u          /* "greater than 4" in the log, checked as < 13 */
#define EVENHUB_MAX_EVENT_CAPTURE 2u

/* msg.cmd values handled here. */
#define EVENHUB_CMD_CREATE 0u
#define EVENHUB_CMD_IMAGE_RAW 3u
#define EVENHUB_CMD_TEXT_UPGRADE 5u
#define EVENHUB_CMD_REBUILD 7u
#define EVENHUB_CMD_SHUTDOWN 9u
#define EVENHUB_CMD_HEARTBEAT 0xcu
#define EVENHUB_CMD_AUDIO_CTRL 0xfu
#define EVENHUB_CMD_MENU_STARTUP_FAILED 0x12u
#define EVENHUB_CMD_OPEN_IMU 0x13u

/* which_Msg_Ctx tags checked here. */
#define EVENHUB_TAG_CREATE 3u
#define EVENHUB_TAG_IMG_RAW 5u
#define EVENHUB_TAG_REBUILD 7u

/* Image raw-data reply status (evenhub_send_image_raw_data_response_4da4a4). */
#define EVENHUB_IMG_STATUS_OK 4u
#define EVENHUB_IMG_STATUS_FAIL 5u

#define EVENHUB_EVENT_IMAGE_REFRESH 0x4c
#define EVENHUB_CONTAINER_IMAGE 2u

/* Decoded protobuf records: only is_event_capture is read here. */
typedef struct {
    uint8_t fields[0x548];
    uint32_t is_event_capture;           /* +0x548 */
    uint8_t tail[8];
} evenhub_pb_list_rec_t;
_Static_assert(sizeof(evenhub_pb_list_rec_t) == 0x554, "pb list record");

typedef struct {
    uint8_t fields[0x34];
    uint32_t is_event_capture;           /* +0x34 */
    uint8_t content[0x3f0];
} evenhub_pb_text_rec_t;
_Static_assert(sizeof(evenhub_pb_text_rec_t) == 0x428, "pb text record");

/* CreateStartUpPageContainer / RebuildPageContainer body (msg +0x04). */
typedef struct {
    uint32_t container_total_num;        /* msg +0x04 */
    uint16_t list_num;                   /* msg +0x08 */
    uint8_t reserved_0a[2];
    evenhub_pb_list_rec_t list[4];       /* msg +0x0c */
    uint16_t text_num;                   /* msg +0x155c */
    uint8_t reserved_155e[2];
    evenhub_pb_text_rec_t text[8];       /* msg +0x1560 */
    uint16_t image_num;                  /* msg +0x36a0 */
    uint8_t reserved_36a2[2];
    uint8_t image[0xb0];                 /* msg +0x36a4 */
} evenhub_pb_create_t;
_Static_assert(sizeof(evenhub_pb_create_t) == 0x3750, "pb create");

/* ImgRawMsg body (msg +0x04). */
typedef struct {
    uint32_t container_id;               /* msg +0x04 */
    char name[16];                       /* msg +0x08 */
    uint32_t session_id;                 /* msg +0x18 Map_Session_Id */
    uint32_t total_size;                 /* msg +0x1c Map_Total_Size */
    uint32_t compress_mode;              /* msg +0x20 */
    uint32_t fragment_index;             /* msg +0x24 Map_Fragment_Index */
    uint32_t fragment_packet_size;       /* msg +0x28 Map_Fragment_Packet_Size */
    uint16_t data_size;                  /* msg +0x2c nanopb bytes size (not used) */
    uint8_t data[1];                     /* msg +0x2e */
} evenhub_pb_img_raw_t;
_Static_assert(offsetof(evenhub_pb_img_raw_t, data) == 0x2a, "pb img raw");

/* IMU control body (msg +0x04). */
typedef struct {
    uint32_t enable;                     /* msg +0x04 */
    uint32_t report_frq;                 /* msg +0x08 */
} evenhub_pb_imu_t;

/* Menu startup failed body (msg +0x04). */
typedef struct {
    uint32_t value;                      /* msg +0x04 */
    char text[1];                        /* msg +0x08 NUL-terminated */
} evenhub_pb_menu_failed_t;

typedef struct {
    uint8_t cmd;                         /* +0x00 */
    uint8_t seq;                         /* +0x01 magicRandom, echoed in replies */
    uint16_t which;                      /* +0x02 which_Msg_Ctx */
    union {
        evenhub_pb_create_t create;
        evenhub_pb_img_raw_t img_raw;
        evenhub_pb_imu_t imu;
        evenhub_pb_menu_failed_t menu_failed;
    } u;                                 /* +0x04 */
    uint32_t startup_widget;             /* +0x3754 */
} evenhub_parser_msg_t;
_Static_assert(sizeof(evenhub_parser_msg_t) == 0x3758, "evenhub msg");

/* Reassembly state kept in the common image container handle (see common_image_container.c). */
typedef struct {
    void *obj;                           /* +0x00 */
    void *image;                         /* +0x04 */
    uint8_t *image_buf;                  /* +0x08 */
    uint8_t *rev_buf;                    /* +0x0c fragment receive buffer */
    uint32_t session_id;                 /* +0x10 0 = no transfer in progress */
    uint32_t total_size;                 /* +0x14 */
    uint32_t compress_mode;              /* +0x18 */
    uint32_t fragment_index;             /* +0x1c last accepted index */
    uint32_t received;                   /* +0x20 bytes received so far */
} evenhub_image_rx_t;

/* EvenHub container list node (evenhub_ui.c). */
typedef struct {
    void *prev;                          /* +0x00 */
    void *next;                          /* +0x04 */
    uint8_t type;                        /* +0x08 */
    uint8_t reserved[3];
    void *pb;                            /* +0x0c */
    void *ui;                            /* +0x10 */
} evenhub_node_t;

/* Startup usage record for key 0x40101: {startup widget id, source}. */
typedef struct {
    uint32_t widget;
    uint32_t source;
} evenhub_start_record_t;

/* "Menu startup failed" packet forwarded to the loading page app 0xffe. */
typedef struct {
    uint8_t type;                        /* +0x00 always 1 */
    uint8_t value;                       /* +0x01 */
    char text[0xda];                     /* +0x02 */
} evenhub_loading_reflash_t;
_Static_assert(sizeof(evenhub_loading_reflash_t) == 0xdc, "loading reflash");

extern evenhub_parser_msg_t g2_evenhub_parser_msg;              /* RAM 0x2033d3f0 */
extern uint32_t g2_evenhub_imu_enabled;                         /* RAM 0x200745bc */
extern const evenhub_start_record_t g2_evenhub_start_record_init; /* ROM 0x78d5a4 = {0, 1} */
extern const uint8_t g2_evenhub_pb_msg_fields_77754c[];          /* ROM 0x77754c nanopb descriptor */

/* nanopb (by-value stream; IAR copies the temporary with 0x439c04). */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;                  /* +0x0c */
} evenhub_pb_istream_t;
extern evenhub_pb_istream_t audio_uart_pb_stream_init(const void *buf, uint32_t len); /* 0x48f49c */
extern uint32_t audio_uart_pb_decode(evenhub_pb_istream_t *, const void *, void *);   /* 0x490120 */

/* Logging. */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

/* libc-like helpers. */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill);      /* memset 0x43c0e4 */
extern void audio_uart_checksum_copy(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* strncpy 0x44b5a0 */
extern uint32_t g2_log_module_length(const char *text);                          /* strlen 0x44a43c */

/* System / sync interface. */
extern uint8_t audio_uart_device_role_get(void);                     /* 0x45a568, 1 = master */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app); /* 1 = app running */
extern uint32_t audio_uart_master_display_start(uint32_t app, const void *data, uint16_t len,
                                                uint32_t flags);     /* 0x464b2e */
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);   /* 0x464bb2 */
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);

/* Rest of evenhub_data_parser.c / evenhub_main.c. */
extern void evenhub_data_mutex_init_4d9b34(void);
extern int32_t evenhub_send_reply_4d9c86(uint8_t cmd, uint8_t seq, uint16_t which, uint32_t value);
extern int32_t evenhub_send_input_event_4da382(uint32_t id, const char *name, int32_t event_code,
                                               uint32_t data);
extern int32_t evenhub_send_image_raw_data_response_4da4a4(uint8_t seq, uint8_t status, uint32_t id,
                                                   const char *name, uint32_t session_id,
                                                   uint32_t total_size, uint32_t compress_mode,
                                                   uint32_t fragment_index,
                                                   uint32_t fragment_packet_size);
extern int32_t evenhub_response_imu_ctr_4da60c(uint8_t seq, uint32_t status);
extern int32_t common_imu_setting_4da720(uint32_t enable, int32_t report_frq);
extern evenhub_node_t *evenhub_container_find_node_by_id_4e0cce(uint32_t id);

static const char dp_tag[] = "evenhub.data_parser"; /* ROM 0x77f3b0 */
static const char dp_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_data_parser.c"; /* ROM 0x6f3434 */
static const char dp_fn[] = "evenhub_data_parser"; /* ROM 0x77f3d8 */
static const char dp_none[] = "(none)"; /* ROM 0x78d59c */

static const char s_enter[] = "evenhub_data_parser len = %d"; /* ROM 0x75fef0 */
static const char s_enter_s[] = "[evenhub.data_parser]evenhub_data_parser len = %d"; /* ROM 0x7295f4 */
static const char s_len0[] = "len is 0,exit."; /* ROM 0x785e60 */
static const char s_len0_s[] = "[evenhub.data_parser]len is 0,exit."; /* ROM 0x75459c */
static const char s_decode[] = "evenhub protobuf decode failed: %s\n"; /* ROM 0x7545c0 */
static const char s_decode_s[] =
    "[evenhub.data_parser]evenhub protobuf decode failed: %s\n"; /* ROM 0x714d64 */
static const char s_cmd[] =
    "evenhub_data_parser cmd = %d, magicRandom = %d, which_Msg_Ctx = %d"; /* ROM 0x7027ac */
static const char s_cmd_s[] = "[evenhub.data_parser]evenhub_data_parser cmd = %d, magicRandom = %d, "
                              "which_Msg_Ctx = %d"; /* ROM 0x6e3148 */

static const char s_create[] =
    "evenhub_data_parser receive create startup page packet from APP"; /* ROM 0x70b4a4 */
static const char s_create_s[] = "[evenhub.data_parser]evenhub_data_parser receive create startup "
                                 "page packet from APP"; /* ROM 0x6e31a0 */
static const char s_not_create[] =
    "which_Msg_Ctx is not CreateMessage_tag. exit! received msgTag is %d"; /* ROM 0x702768 */
static const char s_not_create_s[] = "[evenhub.data_parser]which_Msg_Ctx is not CreateMessage_tag. "
                                     "exit! received msgTag is %d"; /* ROM 0x6e0180 */
static const char s_total[] =
    "ContainerTotalNum is greater than 4. exit! ContainerTotalNum = %d"; /* ROM 0x7027f0 */
static const char s_total_s[] = "[evenhub.data_parser]ContainerTotalNum is greater than 4. exit! "
                                "ContainerTotalNum = %d"; /* ROM 0x6e31f8 */
static const char s_objects[] = "The total number of  objects is greater than 4. exit! list = %d, "
                                "text = %d, image = %d"; /* ROM 0x6e3250 */
static const char s_objects_s[] = "[evenhub.data_parser]The total number of  objects is greater "
                                  "than 4. exit! list = %d, text = %d, image = %d"; /* ROM 0x6a9f54 */
static const char s_capture[] = "The number of containers that can handle events at the end is "
                                "greater than 4. exit! event_capture_count = %d"; /* ROM 0x6d6e80 */
static const char s_capture_s[] =
    "[evenhub.data_parser]The number of containers that can handle events at the end is greater "
    "than 4. exit! event_capture_count = %d"; /* ROM 0x6d4ebc */
static const char s_create_sent[] =
    "evenhub_data_parser send create startup page packet to UI: ret = %d"; /* ROM 0x702834 */
static const char s_create_sent_s[] = "[evenhub.data_parser]evenhub_data_parser send create startup "
                                      "page packet to UI: ret = %d"; /* ROM 0x6e01dc */

static const char s_rebuild[] =
    "evenhub_data_parser receive rebuild page packet from APP"; /* ROM 0x714da0 */
static const char s_rebuild_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive rebuild page packet from APP"; /* ROM 0x6ed018 */
static const char s_not_rebuild[] =
    "which_Msg_Ctx is not RebuildContainer_tag. exit! received msgTag is %d"; /* ROM 0x6fa2ec */
static const char s_not_rebuild_s[] = "[evenhub.data_parser]which_Msg_Ctx is not "
                                      "RebuildContainer_tag. exit! received msgTag is %d"; /* ROM 0x6e0238 */
static const char s_rebuild_sent[] =
    "evenhub_data_parser send rebuild page packet to UI: ret = %d"; /* ROM 0x70b4e4 */
static const char s_rebuild_sent_s[] =
    "[evenhub.data_parser]evenhub_data_parser send rebuild page packet to UI: ret = %d"; /* ROM 0x6e79cc */
static const char s_rebuild_idle[] = "evenhub_data_parser receive rebuild page packet from APP, but "
                                     "app is not running. exit!"; /* ROM 0x6e32a8 */
static const char s_rebuild_idle_s[] = "[evenhub.data_parser]evenhub_data_parser receive rebuild page "
                                       "packet from APP, but app is not running. exit!"; /* ROM 0x6d6ef0 */

static const char s_text[] =
    "evenhub_data_parser receive update text data packet from APP"; /* ROM 0x70b524 */
static const char s_text_s[] = "[evenhub.data_parser]evenhub_data_parser receive update text data "
                               "packet from APP"; /* ROM 0x6e7a20 */

static const char s_shutdown[] =
    "evenhub_data_parser receive shutdown  packet from APP"; /* ROM 0x71ed10 */
static const char s_shutdown_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive shutdown  packet from APP"; /* ROM 0x6f3480 */
static const char s_shutdown_sent[] =
    "evenhub_data_parser send shutdown packet to UI: ret = %d"; /* ROM 0x714ddc */
static const char s_shutdown_sent_s[] =
    "[evenhub.data_parser]evenhub_data_parser send shutdown packet to UI: ret = %d"; /* ROM 0x6ed068 */
static const char s_shutdown_idle[] = "evenhub_data_parser receive shutdown packet from APP, but app "
                                      "is not running. exit!"; /* ROM 0x6e7a74 */
static const char s_shutdown_idle_s[] = "[evenhub.data_parser]evenhub_data_parser receive shutdown "
                                        "packet from APP, but app is not running. exit!"; /* ROM 0x6c94fc */

static const char s_heartbeat[] =
    "evenhub_data_parser receive heartbeat packet from APP"; /* ROM 0x71ed48 */
static const char s_heartbeat_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive heartbeat packet from APP"; /* ROM 0x6f34cc */
static const char s_heartbeat_sent[] =
    "evenhub_data_parser send heartbeat packet to UI: ret = %d"; /* ROM 0x714e18 */
static const char s_heartbeat_sent_s[] =
    "[evenhub.data_parser]evenhub_data_parser send heartbeat packet to UI: ret = %d"; /* ROM 0x6ed0b8 */

static const char s_audio[] =
    "evenhub_data_parser receive audio control packet from APP"; /* ROM 0x714e54 */
static const char s_audio_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive audio control packet from APP"; /* ROM 0x6ed108 */
static const char s_audio_sent[] =
    "evenhub_data_parser send audio control packet to UI: ret = %d"; /* ROM 0x70b564 */
static const char s_audio_sent_s[] = "[evenhub.data_parser]evenhub_data_parser send audio control "
                                     "packet to UI: ret = %d"; /* ROM 0x6e7ac8 */

static const char s_imu[] = "evenhub_data_parser receive open IMU packet from APP"; /* ROM 0x71ed80 */
static const char s_imu_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive open IMU packet from APP"; /* ROM 0x6f3518 */
static const char s_imu_sent[] =
    "evenhub_data_parser send open IMU packet to UI,en = %d,report frq = %d"; /* ROM 0x6fa334 */
static const char s_imu_sent_s[] = "[evenhub.data_parser]evenhub_data_parser send open IMU packet "
                                   "to UI,en = %d,report frq = %d"; /* ROM 0x6e0294 */
static const char s_imu_open[] = "evenhub_data_parser open IMU success"; /* ROM 0x749f24 */
static const char s_imu_open_s[] =
    "[evenhub.data_parser]evenhub_data_parser open IMU success"; /* ROM 0x714e90 */
static const char s_imu_close[] = "evenhub_data_parser close IMU"; /* ROM 0x75ff10 */
static const char s_imu_close_s[] = "[evenhub.data_parser]evenhub_data_parser close IMU"; /* ROM 0x729628 */

static const char s_menu_failed[] =
    "evenhub_data_parser receive menu startup failed packet from APP"; /* ROM 0x70b5a4 */
static const char s_menu_failed_s[] = "[evenhub.data_parser]evenhub_data_parser receive menu startup "
                                      "failed packet from APP"; /* ROM 0x6e3300 */
static const char s_loading_sent[] =
    "evenhub_data_parser send loading page reflash packet to UI: ret = %d"; /* ROM 0x6fa37c */
static const char s_loading_sent_s[] = "[evenhub.data_parser]evenhub_data_parser send loading page "
                                       "reflash packet to UI: ret = %d"; /* ROM 0x6e02f0 */

static const char s_img[] =
    "evenhub_data_parser receive update image raw data packet from APP"; /* ROM 0x702878 */
static const char s_img_s[] = "[evenhub.data_parser]evenhub_data_parser receive update image raw "
                              "data packet from APP"; /* ROM 0x6e3358 */
static const char s_not_img[] =
    "which_Msg_Ctx is not ImgRawMsg_tag. exit! received msgTag is %d"; /* ROM 0x70b5e4 */
static const char s_not_img_s[] = "[evenhub.data_parser]which_Msg_Ctx is not ImgRawMsg_tag. exit! "
                                  "received msgTag is %d"; /* ROM 0x6e33b0 */
static const char s_img_info[] = "id = %d,name = %s,session_id = %d,total_size = %d,compress_mode = "
                                 "%d,fragment_index = %d,fragment_packet_size = %d"; /* ROM 0x69f9dc */
static const char s_img_info_s[] =
    "[evenhub.data_parser]id = %d,name = %s,session_id = %d,total_size = %d,compress_mode = %d,"
    "fragment_index = %d,fragment_packet_size = %d"; /* ROM 0x6d4768 */
static const char s_not_found[] =
    "evenhub_container_find_node_by_id: container_id = %d not found"; /* ROM 0x70b624 */
static const char s_not_found_s[] = "[evenhub.data_parser]evenhub_container_find_node_by_id: "
                                    "container_id = %d not found"; /* ROM 0x6e7b1c */
static const char s_not_image[] =
    "evenhub_container_find_node_by_id: container_id = %d is not a image container"; /* ROM 0x6ed158 */
static const char s_not_image_s[] = "[evenhub.data_parser]evenhub_container_find_node_by_id: "
                                    "container_id = %d is not a image container"; /* ROM 0x6da7a0 */
static const char s_idx0[] = "evenhub_data_parser receive update image raw data packet from APP "
                             ",index is 0. index = %d"; /* ROM 0x6e034c */
static const char s_idx0_s[] = "[evenhub.data_parser]evenhub_data_parser receive update image raw "
                               "data packet from APP ,index is 0. index = %d"; /* ROM 0x6d6f60 */
static const char s_idx_match[] = "evenhub_data_parser receive update image raw data packet from APP "
                                  ",index is match. index = %d"; /* ROM 0x6dd294 */
static const char s_idx_match_s[] = "[evenhub.data_parser]evenhub_data_parser receive update image "
                                    "raw data packet from APP ,index is match. index = %d"; /* ROM 0x69fdd4 */
static const char s_idx_not0[] =
    "evenhub_data_parser receive update image raw data packet from APP, but Map_Fragment_Index is "
    "not 0. exit! Map_Fragment_Index = %d"; /* ROM 0x6d4f40 */
static const char s_idx_not0_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Fragment_Index is not 0. exit! Map_Fragment_Index = %d"; /* ROM 0x6d3850 */
static const char s_session[] =
    "evenhub_data_parser receive update image raw data packet from APP, but Map_Session_Id is not "
    "match. exit! Map_Session_Id = %d, received Map_Session_Id = %d"; /* ROM 0x6d37b4 */
static const char s_session_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Session_Id is not match. exit! Map_Session_Id = %d, received Map_Session_Id = %d"; /* ROM 0x6d1ec4 */
static const char s_restart[] =
    "evenhub_data_parser receive update image raw data packet from APP, but Map_Fragment_Index is "
    "0. clear the original data"; /* ROM 0x6d60b0 */
static const char s_restart_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Fragment_Index is 0. clear the original data"; /* ROM 0x6d3bd0 */
static const char s_idx_mismatch[] =
    "evenhub_data_parser receive update image raw data packet from APP, but Map_Fragment_Index is "
    "not match. exit! Map_Fragment_Index = %d, received Map_Fragment_Index = %d"; /* ROM 0x6d2928 */
static const char s_idx_mismatch_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Fragment_Index is not match. exit! Map_Fragment_Index = %d, received Map_Fragment_Index = "
    "%d"; /* ROM 0x6d1608 */
static const char s_overflow[] =
    "evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Fragment_Packet_Size is greater than Map_Total_Size. exit! Map_Fragment_Packet_Size = %d, "
    "Map_Total_Size = %d"; /* ROM 0x6d1848 */
static const char s_overflow_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive update image raw data packet from APP, but "
    "Map_Fragment_Packet_Size is greater than Map_Total_Size. exit! Map_Fragment_Packet_Size = %d, "
    "Map_Total_Size = %d"; /* ROM 0x6d1074 */
static const char s_unknown[] =
    "evenhub_data_parser receive unknown command, exit. cmd = %d"; /* ROM 0x714ecc */
static const char s_unknown_s[] =
    "[evenhub.data_parser]evenhub_data_parser receive unknown command, exit. cmd = %d"; /* ROM 0x6e7b70 */

/* Both sinks are tested separately and the arguments are evaluated per sink, as in stock. */
#define DP_LOG(level, line, cflags, text, short_text, ...)                                    \
    do {                                                                                      \
        if ((audio_log_flags() & 2u) != 0u)                                                   \
            audio_log_extended((level), dp_tag, dp_file, dp_fn, (line), (text), ##__VA_ARGS__); \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                 \
            (void)compress_log_output((cflags), (short_text), (short_text), ##__VA_ARGS__);   \
    } while (0)

/* App-forwarding helper semantics: forward only on the master arm while the EvenHub UI app runs. */
static bool evenhub_ui_running(uint32_t app)
{
    return audio_uart_device_role_get() == 1u && audio_quicklist_refresh_enabled_4434d0(app) == 1u;
}

/* Shared CreateMessage/RebuildContainer validation (inlined twice in stock). Returns the number
 * of event-capturing containers or a negative value when the object counts are too large. */
static int32_t evenhub_count_event_capture(const evenhub_pb_create_t *c, uint32_t line_total,
                                           uint32_t line_objects)
{
    uint8_t count = 0u;
    uint8_t i;

    if (c->container_total_num >= EVENHUB_MAX_OBJECTS) {
        DP_LOG(1, line_total, 0x4400000u, s_total, s_total_s, c->container_total_num);
        return -1;
    }
    if ((int32_t)((uint32_t)c->text_num + c->list_num + c->image_num) >= (int32_t)EVENHUB_MAX_OBJECTS) {
        DP_LOG(1, line_objects, 0x4c00000u, s_objects, s_objects_s, (uint32_t)c->list_num,
               (uint32_t)c->text_num, (uint32_t)c->image_num);
        return -1;
    }
    for (i = 0u; i < c->list_num; i++) {
        if (c->list[i].is_event_capture == 1u)
            count++;
    }
    for (i = 0u; i < c->text_num; i++) {
        if (c->text[i].is_event_capture == 1u)
            count++;
    }
    return (int32_t)count;
}

static void evenhub_img_reply(uint8_t seq, uint8_t status, const evenhub_pb_img_raw_t *m)
{
    (void)evenhub_send_image_raw_data_response_4da4a4(seq, status, m->container_id, m->name, m->session_id,
                                              m->total_size, m->compress_mode, m->fragment_index,
                                              m->fragment_packet_size);
}

/* Start a new transfer from fragment 0 and acknowledge it. */
static void evenhub_img_begin(evenhub_image_rx_t *rx, uint8_t seq, const evenhub_pb_img_raw_t *m)
{
    rx->session_id = m->session_id;
    rx->total_size = m->total_size;
    rx->compress_mode = m->compress_mode;
    rx->fragment_index = m->fragment_index;
    rx->received = m->fragment_packet_size;
    audio_uart_checksum_copy(rx->rev_buf, m->data, m->fragment_packet_size);
    evenhub_img_reply(seq, EVENHUB_IMG_STATUS_OK, m);
}

/* Last fragment received: close the session and tell the UI to refresh the image. */
static void evenhub_img_complete(evenhub_image_rx_t *rx, uint32_t line, uint32_t id,
                                 const evenhub_pb_img_raw_t *m)
{
    DP_LOG(3, line, 0xc400000u, s_idx_match, s_idx_match_s, m->fragment_index);
    rx->session_id = 0u;
    if (evenhub_ui_running(EVENHUB_APP_ID))
        (void)evenhub_send_input_event_4da382(id, m->name, EVENHUB_EVENT_IMAGE_REFRESH, 0u);
}

static int32_t evenhub_parse_image_raw(evenhub_parser_msg_t *msg, uint8_t seq)
{
    const evenhub_pb_img_raw_t *m = &msg->u.img_raw;
    evenhub_node_t *node;
    evenhub_image_rx_t *rx;
    uint32_t id;

    DP_LOG(3, 0x2e7, 0xc000000u, s_img, s_img_s);
    if (msg->which != EVENHUB_TAG_IMG_RAW) {
        DP_LOG(1, 0x2e9, 0x4400000u, s_not_img, s_not_img_s, (uint32_t)msg->which);
        evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        return -1;
    }
    id = m->container_id;
    DP_LOG(3, 0x2f7, 0xdc00000u, s_img_info, s_img_info_s, id, m->name, m->session_id,
           m->total_size, m->compress_mode, m->fragment_index, m->fragment_packet_size);
    node = evenhub_container_find_node_by_id_4e0cce(id);
    if (node == NULL) {
        DP_LOG(1, 0x2fb, 0x4400000u, s_not_found, s_not_found_s, id);
        evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        return -4;
    }
    if (node->type != EVENHUB_CONTAINER_IMAGE) {
        DP_LOG(1, 0x305, 0x4400000u, s_not_image, s_not_image_s, id);
        evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        return -4;
    }
    rx = (evenhub_image_rx_t *)node->ui;

    if (rx->session_id == 0u) {
        /* No transfer in progress: only fragment 0 may open one. */
        if (m->fragment_index != 0u) {
            DP_LOG(2, 0x328, 0x8400000u, s_idx_not0, s_idx_not0_s, m->fragment_index);
            rx->session_id = 0u;
            evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
            return 0; /* stock returns the reply result here */
        }
        DP_LOG(3, 0x312, 0xc400000u, s_idx0, s_idx0_s, m->fragment_index);
        evenhub_img_begin(rx, seq, m);
        if (rx->received == rx->total_size)
            evenhub_img_complete(rx, 0x31f, id, m);
        return 0;
    }

    if (rx->session_id != m->session_id) {
        DP_LOG(2, 0x333, 0x8800000u, s_session, s_session_s, rx->session_id, m->session_id);
        if (m->fragment_index == 0u) {
            /* A new session restarting at fragment 0 replaces the old one. */
            DP_LOG(3, 0x335, 0xc000000u, s_restart, s_restart_s);
            evenhub_img_begin(rx, seq, m);
        } else {
            DP_LOG(2, 0x342, 0x8400000u, s_idx_not0, s_idx_not0_s, m->fragment_index);
            rx->session_id = 0u;
            evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        }
        return 0; /* stock returns the reply result here */
    }

    if (rx->fragment_index != m->fragment_index - 1u || rx->total_size != m->total_size ||
        rx->compress_mode != m->compress_mode) {
        DP_LOG(2, 0x34c, 0x8800000u, s_idx_mismatch, s_idx_mismatch_s, rx->fragment_index,
               m->fragment_index);
        rx->session_id = 0u;
        evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        return -4;
    }
    if (rx->total_size < m->fragment_packet_size + rx->received) {
        DP_LOG(1, 0x357, 0x4800000u, s_overflow, s_overflow_s, rx->received, rx->total_size);
        rx->session_id = 0u;
        evenhub_img_reply(seq, EVENHUB_IMG_STATUS_FAIL, m);
        return -4;
    }
    DP_LOG(3, 0x360, 0xc400000u, s_idx_match, s_idx_match_s, m->fragment_index);
    rx->fragment_index = m->fragment_index;
    audio_uart_checksum_copy(rx->rev_buf + rx->received, m->data, m->fragment_packet_size);
    rx->received = m->fragment_packet_size + rx->received;
    evenhub_img_reply(seq, EVENHUB_IMG_STATUS_OK, m);
    if (rx->received == rx->total_size)
        evenhub_img_complete(rx, 0x36a, id, m);
    return 0;
}

/* Returns 0 on success, -1 bad tag / unknown command, -2 empty input, -3 decode failure,
 * -4 rejected content. Paths that only forward to the UI fall out of the stock function without
 * an explicit return value (r0 is whatever the last call left); they return 0 here. */
int32_t evenhub_data_parser_4da834(const uint8_t *data, uint32_t len)
{
    evenhub_parser_msg_t *msg;
    evenhub_pb_istream_t stream;
    uint8_t cmd;
    uint8_t seq;
    uint16_t which;
    int32_t count;
    uint32_t ret;

    evenhub_data_mutex_init_4d9b34();
    DP_LOG(4, 0x210, 0x10400000u, s_enter, s_enter_s, len);
    if (len == 0u) {
        DP_LOG(1, 0x212, 0x4000000u, s_len0, s_len0_s);
        return -2;
    }

    msg = &g2_evenhub_parser_msg;
    audio_uart_buffer_zero(msg, sizeof(*msg), 0u);
    stream = audio_uart_pb_stream_init(data, len);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_evenhub_pb_msg_fields_77754c, msg) == 0u) {
        DP_LOG(1, 0x21a, 0x4400000u, s_decode, s_decode_s,
               (stream.errmsg != NULL) ? stream.errmsg : dp_none);
        return -3;
    }

    cmd = msg->cmd;
    seq = msg->seq;
    which = msg->which;
    DP_LOG(4, 0x221, 0x10c00000u, s_cmd, s_cmd_s, (uint32_t)cmd, (uint32_t)seq, (uint32_t)which);

    switch (cmd) {
    case EVENHUB_CMD_CREATE:
        DP_LOG(4, 0x225, 0x10000000u, s_create, s_create_s);
        if (which != EVENHUB_TAG_CREATE) {
            DP_LOG(1, 0x228, 0x4400000u, s_not_create, s_not_create_s, (uint32_t)which);
            return -1;
        }
        count = evenhub_count_event_capture(&msg->u.create, 0x22f, 0x237);
        if (count < 0) {
            (void)evenhub_send_reply_4d9c86(1u, seq, 4u, 2u);
            return -4;
        }
        if ((uint32_t)count >= EVENHUB_MAX_EVENT_CAPTURE) {
            DP_LOG(1, 0x24d, 0x4400000u, s_capture, s_capture_s, (uint32_t)count);
            (void)evenhub_send_reply_4d9c86(1u, seq, 4u, 1u);
            return -4;
        }
        /* Only a master arm whose EvenHub app is not yet running starts it with this packet. */
        if (audio_uart_device_role_get() == 1u &&
            audio_quicklist_refresh_enabled_4434d0(EVENHUB_APP_ID) == 0u) {
            evenhub_start_record_t record;

            ret = audio_uart_master_display_start(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            record = g2_evenhub_start_record_init;
            record.widget = msg->startup_widget;
            audio_uart_ring_wear_persist_48eb32(EVENHUB_START_RECORD_KEY, 2u, &record);
            DP_LOG(4, 0x256, 0x10400000u, s_create_sent, s_create_sent_s, ret);
        }
        return 0;

    case EVENHUB_CMD_REBUILD:
        DP_LOG(4, 0x25e, 0x10000000u, s_rebuild, s_rebuild_s);
        if (which != EVENHUB_TAG_REBUILD) {
            DP_LOG(1, 0x261, 0x4400000u, s_not_rebuild, s_not_rebuild_s, (uint32_t)which);
            return -1;
        }
        count = evenhub_count_event_capture(&msg->u.create, 0x268, 0x270);
        if (count < 0) {
            (void)evenhub_send_reply_4d9c86(8u, seq, 8u, 7u);
            return -4;
        }
        if ((uint32_t)count >= EVENHUB_MAX_EVENT_CAPTURE) {
            DP_LOG(1, 0x286, 0x4400000u, s_capture, s_capture_s, (uint32_t)count);
            (void)evenhub_send_reply_4d9c86(8u, seq, 8u, 7u);
            return -4;
        }
        if (evenhub_ui_running(EVENHUB_APP_ID)) {
            ret = audio_uart_master_display_refresh(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            DP_LOG(4, 0x28e, 0x10400000u, s_rebuild_sent, s_rebuild_sent_s, ret);
        } else {
            DP_LOG(1, 0x290, 0x4000000u, s_rebuild_idle, s_rebuild_idle_s);
            (void)evenhub_send_reply_4d9c86(8u, seq, 8u, 7u);
        }
        return 0;

    case EVENHUB_CMD_TEXT_UPGRADE:
        DP_LOG(4, 0x29b, 0x10000000u, s_text, s_text_s);
        if (evenhub_ui_running(EVENHUB_APP_ID)) {
            ret = audio_uart_master_display_refresh(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            DP_LOG(4, 0x29e, 0x10400000u, s_rebuild_sent, s_rebuild_sent_s, ret);
            return 0;
        }
        /* Stock reuses the rebuild "not running" message here. */
        DP_LOG(1, 0x2a0, 0x4000000u, s_rebuild_idle, s_rebuild_idle_s);
        return evenhub_send_reply_4d9c86(6u, seq, 10u, 9u);

    case EVENHUB_CMD_SHUTDOWN:
        DP_LOG(4, 0x2a8, 0x10000000u, s_shutdown, s_shutdown_s);
        if (evenhub_ui_running(EVENHUB_APP_ID)) {
            ret = audio_uart_master_display_refresh(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            DP_LOG(4, 0x2ab, 0x10400000u, s_shutdown_sent, s_shutdown_sent_s, ret);
            return 0;
        }
        DP_LOG(1, 0x2ad, 0x4000000u, s_shutdown_idle, s_shutdown_idle_s);
        return evenhub_send_reply_4d9c86(10u, seq, 0xcu, 0xbu);

    case EVENHUB_CMD_HEARTBEAT:
        DP_LOG(4, 0x2b5, 0x10000000u, s_heartbeat, s_heartbeat_s);
        if (evenhub_ui_running(EVENHUB_APP_ID)) {
            ret = audio_uart_master_display_refresh(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            DP_LOG(4, 0x2b8, 0x10400000u, s_heartbeat_sent, s_heartbeat_sent_s, ret);
        }
        return 0;

    case EVENHUB_CMD_AUDIO_CTRL:
        DP_LOG(4, 0x2be, 0x10000000u, s_audio, s_audio_s);
        if (evenhub_ui_running(EVENHUB_APP_ID)) {
            ret = audio_uart_master_display_refresh(EVENHUB_APP_ID, data, (uint16_t)len, 0u);
            DP_LOG(4, 0x2c1, 0x10400000u, s_audio_sent, s_audio_sent_s, ret);
        }
        return 0;

    case EVENHUB_CMD_OPEN_IMU:
        DP_LOG(4, 0x2c7, 0x10000000u, s_imu, s_imu_s);
        if (!evenhub_ui_running(EVENHUB_APP_ID))
            return 0;
        DP_LOG(4, 0x2c9, 0x10800000u, s_imu_sent, s_imu_sent_s, msg->u.imu.enable,
               msg->u.imu.report_frq);
        (void)common_imu_setting_4da720(msg->u.imu.enable, msg->u.imu.report_frq);
        if (msg->u.imu.enable == 1u) {
            DP_LOG(3, 0x2cc, 0xc000000u, s_imu_open, s_imu_open_s);
            g2_evenhub_imu_enabled = 1u;
        } else {
            DP_LOG(3, 0x2cf, 0xc000000u, s_imu_close, s_imu_close_s);
            g2_evenhub_imu_enabled = 0u;
        }
        return evenhub_response_imu_ctr_4da60c(seq, msg->u.imu.enable);

    case EVENHUB_CMD_MENU_STARTUP_FAILED:
        DP_LOG(4, 0x2d8, 0x10000000u, s_menu_failed, s_menu_failed_s);
        if (evenhub_ui_running(EVENHUB_LOADING_APP_ID)) {
            evenhub_loading_reflash_t pkt;
            const char *text = msg->u.menu_failed.text;

            audio_uart_buffer_zero(&pkt, sizeof(pkt), 0u);
            audio_uart_buffer_zero(&pkt, sizeof(pkt), 0u); /* cleared twice in stock */
            pkt.type = 1u;
            pkt.value = (uint8_t)msg->u.menu_failed.value;
            (void)audio_settings_copy_text(pkt.text, text, g2_log_module_length(text));
            ret = audio_uart_master_display_refresh(EVENHUB_LOADING_APP_ID, &pkt,
                                                    (uint16_t)(g2_log_module_length(text) + 2u), 0u);
            DP_LOG(4, 0x2e1, 0x10400000u, s_loading_sent, s_loading_sent_s, ret);
        }
        return 0;

    case EVENHUB_CMD_IMAGE_RAW:
        return evenhub_parse_image_raw(msg, seq);

    default:
        DP_LOG(1, 0x37d, 0x4400000u, s_unknown, s_unknown_s, (uint32_t)cmd);
        return -1;
    }
}
