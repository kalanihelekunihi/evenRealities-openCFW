/* Navigation protobuf receive path and two shared senders, part of stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\navigation\navigation_data_handler.c
 * (path ROM 0x6e8b84, log tag "navigation.datahandler" ROM 0x7798bc).
 * Native 0x587186..0x587237 (navigation_send_type_9_shared),
 * 0x587240..0x5872b7 (navigation_send_type_1_shared),
 * 0x5872f4..0x5882e5 (navigation_data_dispatch, stock name
 * navigation_data_handler, with inline pools 0x588014..0x58803b and
 * 0x5881b0..0x5881c3) and 0x588388..0x588485 (navigation_icon_name_for_code);
 * literal pools 0x587238..0x58723f, 0x5872b8..0x5872f3 (shared with the other
 * senders), 0x5882e8..0x588387 and 0x588488..0x588513. The remaining
 * navigation_send_type_* senders (0x586448..0x587185) live in the same TU.
 *
 * Every navigation message is one nanopb oneof (descriptor ROM 0x7798a4,
 * 0x2024 bytes): [type u8][magic u8][which u16][payload]. Received messages
 * are decoded into RAM 0x20356db0; transmitted ones are built in RAM
 * 0x20358dd4 and encoded into the 10000-byte buffer RAM 0x20350430, then sent
 * as PB type 1 / command 8. The dispatcher forwards each received command to
 * the master display side as a 6-byte page message (app 8) on the same
 * [cmd][input][value] layout navigation_ui_reflash_page_handler parses, and
 * reassembles the fragmented mini map (<= 18000 bytes) and max map
 * (<= 60000 bytes) into the UI record at RAM 0x202c0d70, acknowledging each
 * fragment with send type 8 / 9 (status 0 ok, 7 error). */
#include <stdint.h>
#include <stddef.h>

#define WAIT_FOREVER 0xffffffffu

#define NAV_APP_ID          8u
#define NAV_PB_TYPE         1u
#define NAV_PB_COMMAND      8u
#define NAV_MSG_SIZE        0x2024u
#define NAV_TX_BUF_SIZE     10000u
#define NAV_MAX_LOCATIONS   20
#define NAV_MINI_MAP_SIZE   18000u   /* 0x4650 */
#define NAV_MAX_MAP_SIZE    60000u   /* 0xea60 */
#define NAV_START_RECORD_KEY 0x40101u

#define NAV_STATUS_OK       0u
#define NAV_STATUS_ERROR    7u

/* Received command ids (msg.type). */
enum {
    NAV_RX_HEARTBEAT = 0u,
    NAV_RX_LOCATION_LIST = 2u,
    NAV_RX_NONE_LOCATION_LIST = 3u,
    NAV_RX_START = 5u,
    NAV_RX_ERROR_INFO = 6u,
    NAV_RX_BASIC_INFO = 7u,
    NAV_RX_MINI_MAP = 8u,
    NAV_RX_MAX_MAP = 9u,
    NAV_RX_RECALCULATING = 10u,
    NAV_RX_COMPLETE = 11u,
    NAV_RX_EXIT = 12u,
};

/* ---- nanopb message (0x2024 bytes) ---- */

/* type 2, which 4: location list */
typedef struct {
    uint32_t total;                       /* +0x004 loop bound */
    uint16_t name_count;                  /* +0x008 */
    char name[NAV_MAX_LOCATIONS][0x40];   /* +0x00a */
    uint16_t icon_count;                  /* +0x50a */
    uint32_t icon_index[NAV_MAX_LOCATIONS]; /* +0x50c */
} g2_nav_pb_location_list_t;

/* type 6: error info, only +0x48 is forwarded */
typedef struct {
    uint32_t field_04;                    /* +0x004 */
    char text[0x40];                      /* +0x008 */
    uint32_t value;                       /* +0x048 */
} g2_nav_pb_error_info_t;

/* type 7: basic info, same field offsets as the staging record */
typedef struct {
    uint32_t turn_icon;                   /* +0x004 navigation_icon_name_for_code */
    char distance[0x40];                  /* +0x008 */
    char road_name[0x40];                 /* +0x048 */
    char spend_time[0x40];                /* +0x088 */
    char remain_distance[0x40];           /* +0x0c8 */
    char eta_time[0x40];                  /* +0x108 */
    char speed[0x40];                     /* +0x148 */
    uint32_t navigate_work_method;        /* +0x188 */
} g2_nav_pb_basic_info_t;

/* type 8: mini map fragment */
typedef struct {
    uint32_t total_size;                  /* +0x0004 */
    uint32_t compress_mode;               /* +0x0008 */
    uint16_t size;                        /* +0x000c */
    uint8_t bytes[0x2000];                /* +0x000e */
    uint8_t reserved_200e[2];
    uint32_t param_2010;                  /* +0x2010 kept in UI +0x198 */
    uint32_t param_2014;                  /* +0x2014 kept (u8) in UI +0x47ec */
    uint32_t session_id;                  /* +0x2018 */
    uint32_t fragment_index;              /* +0x201c */
    uint32_t param_2020;                  /* +0x2020 echoed in the ack */
} g2_nav_pb_mini_map_t;

/* type 9: max map fragment */
typedef struct {
    uint32_t session_id;                  /* +0x004 */
    uint32_t total_size;                  /* +0x008 */
    uint32_t compress_mode;               /* +0x00c */
    uint32_t fragment_index;              /* +0x010 */
    uint32_t param_14;                    /* +0x014 echoed in the ack */
    uint16_t size;                        /* +0x018 */
    uint8_t bytes[0x1000];                /* +0x01a */
    uint8_t status;                       /* +0x101a ack status (tx only) */
} g2_nav_pb_max_map_t;

typedef struct {
    uint8_t type;                         /* +0x000 */
    uint8_t magic;                        /* +0x001 */
    uint16_t which;                       /* +0x002 oneof tag */
    union {
        g2_nav_pb_location_list_t location_list;
        g2_nav_pb_error_info_t error_info;
        g2_nav_pb_basic_info_t basic_info;
        g2_nav_pb_mini_map_t mini_map;
        g2_nav_pb_max_map_t max_map;
        struct {
            uint8_t value;                /* +0x004 */
        } type1;
        uint8_t raw[NAV_MSG_SIZE - 4u];
    } u;                                  /* +0x004 */
} g2_nav_pb_msg_t;
_Static_assert(sizeof(g2_nav_pb_msg_t) == NAV_MSG_SIZE, "stock message is 0x2024 bytes");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.location_list.name) == 0x00a, "location names");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.location_list.icon_index) == 0x50c, "location icons");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.error_info.value) == 0x048, "error info value");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.basic_info.navigate_work_method) == 0x188, "work method");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.mini_map.bytes) == 0x00e, "mini map bytes");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.mini_map.param_2010) == 0x2010, "mini map params");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.mini_map.param_2020) == 0x2020, "mini map tail");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.max_map.bytes) == 0x01a, "max map bytes");
_Static_assert(offsetof(g2_nav_pb_msg_t, u.max_map.status) == 0x101a, "max map status");

/* nanopb 0.4 streams */
typedef struct {
    void *callback;
    void *state;
    uint32_t bytes_left;
    const char *errmsg;    /* +0x0c */
} g2_pb_istream_t;
typedef struct {
    void *callback;
    void *state;
    uint32_t max_size;
    uint32_t bytes_written; /* +0x0c */
    const char *errmsg;
} g2_pb_ostream_t;
_Static_assert(sizeof(g2_pb_istream_t) == 16u, "nanopb istream");
_Static_assert(sizeof(g2_pb_ostream_t) == 20u, "nanopb ostream");

/* ---- UI side records (layouts shared with ui/a-49 / a-50) ---- */

/* Location list (RAM 0x20376c38, 0x55c bytes). */
typedef struct {
    uint32_t count;                               /* +0x000 */
    uint8_t header_04[2];                         /* +0x004 */
    char name[NAV_MAX_LOCATIONS][0x40];           /* +0x006 */
    uint8_t reserved_506[2];                      /* +0x506 */
    uint32_t icon_type[NAV_MAX_LOCATIONS];        /* +0x508 */
    uint8_t reserved_558[4];                      /* +0x558 */
} g2_navigation_location_list_t;
_Static_assert(sizeof(g2_navigation_location_list_t) == 0x55c, "stock memset size");

/* Navigation info staging record (RAM 0x2037bdd0). */
typedef struct {
    uint8_t valid;                 /* +0x000 */
    uint8_t reserved_01[3];
    uint32_t field_04;             /* +0x004 turn icon code */
    char distance[0x40];           /* +0x008 */
    char road_name[0x40];          /* +0x048 */
    char spend_time[0x40];         /* +0x088 */
    char remain_distance[0x40];    /* +0x0c8 */
    char eta_time[0x40];           /* +0x108 */
    char speed[0x40];              /* +0x148 */
    uint32_t navigate_work_method; /* +0x188 */
} g2_navigation_info_t;
_Static_assert(sizeof(g2_navigation_info_t) == 0x18c, "navigation info record");

/* UI navigation record (RAM 0x202c0d70). */
typedef struct {
    g2_navigation_info_t info;                 /* +0x0000 */
    uint8_t mini_map_ready;                    /* +0x018c */
    uint8_t reserved_18d[3];
    uint32_t mini_map_size;                    /* +0x0190 */
    uint32_t mini_map_compress_mode;           /* +0x0194 */
    uint32_t mini_map_param_198;               /* +0x0198 from rx +0x2010 */
    uint8_t mini_map_data[NAV_MINI_MAP_SIZE];  /* +0x019c */
    uint8_t mini_map_param_47ec;               /* +0x47ec from rx +0x2014 */
    uint8_t max_map_ready;                     /* +0x47ed */
    uint8_t reserved_47ee[2];
    uint32_t max_map_size;                     /* +0x47f0 */
    uint32_t max_map_compress_mode;            /* +0x47f4 */
    uint8_t max_map_data[NAV_MAX_MAP_SIZE];    /* +0x47f8 */
} g2_navigation_ui_data_t;
_Static_assert(offsetof(g2_navigation_ui_data_t, mini_map_data) == 0x19c, "mini map data");
_Static_assert(offsetof(g2_navigation_ui_data_t, max_map_ready) == 0x47ed, "max map flag");
_Static_assert(sizeof(g2_navigation_ui_data_t) == 0x13258, "navigation ui record");

/* Mini map reassembly cache (RAM 0x20329600, 0x4674 bytes). */
typedef struct {
    uint32_t reserved_00;          /* +0x00 */
    uint32_t session_id;           /* +0x04 */
    uint32_t total_size;           /* +0x08 */
    uint32_t compress_mode;        /* +0x0c */
    uint32_t param_10;             /* +0x10 */
    uint32_t param_14;             /* +0x14 */
    uint32_t fragment_index;       /* +0x18 */
    uint32_t param_1c;             /* +0x1c */
    uint32_t received;             /* +0x20 */
    uint8_t data[NAV_MINI_MAP_SIZE]; /* +0x24 */
} g2_nav_mini_map_cache_t;
_Static_assert(sizeof(g2_nav_mini_map_cache_t) == 0x4674, "stock memset size");

/* Max map reassembly cache (RAM 0x202e4fc8, 0xea7c bytes). */
typedef struct {
    uint32_t reserved_00;          /* +0x00 */
    uint32_t session_id;           /* +0x04 */
    uint32_t total_size;           /* +0x08 */
    uint32_t compress_mode;        /* +0x0c */
    uint32_t fragment_index;       /* +0x10 */
    uint32_t param_14;             /* +0x14 never written here */
    uint32_t received;             /* +0x18 */
    uint8_t data[NAV_MAX_MAP_SIZE]; /* +0x1c */
} g2_nav_max_map_cache_t;
_Static_assert(sizeof(g2_nav_max_map_cache_t) == 0xea7c, "stock memset size");

/* Page message to the master display: [cmd][input][value...], 6 bytes sent. */
typedef struct {
    uint8_t cmd;
    uint8_t input;
    uint8_t value[8];
} g2_nav_page_msg_t;
_Static_assert(sizeof(g2_nav_page_msg_t) == 10u, "stock clears 10 bytes");

/* Usage record {app, reason}. */
typedef struct {
    uint32_t app;
    uint32_t reason;
} g2_nav_usage_record_t;

/* ---- RAM / ROM ---- */
extern void *g2_navigation_mutex;                                       /* RAM 0x2007471c */
extern uint32_t g2_nav_var_20074758;                                    /* RAM 0x20074758 location list valid */
extern uint8_t g2_navigation_pb_rx_msg_20356db0[NAV_MSG_SIZE];          /* RAM 0x20356db0 */
extern uint8_t g2_nav_msg_shared_20358dd4[NAV_MSG_SIZE];          /* RAM 0x20358dd4 */
extern uint8_t g2_nav_tx_buf_20350430[NAV_TX_BUF_SIZE];       /* RAM 0x20350430 */
extern g2_navigation_location_list_t g2_navigation_location_list_20376c38; /* RAM 0x20376c38 */
extern g2_navigation_info_t g2_navigation_info_staging_2037bdd0;       /* RAM 0x2037bdd0 */
extern g2_navigation_ui_data_t g2_navigation_ui_data_202c0d70;          /* RAM 0x202c0d70 */
extern uint8_t g2_nav_buf_20329600[0x4674];                             /* RAM 0x20329600 mini map cache */
extern uint8_t g2_nav_buf_202e4fc8[0xea7c];                             /* RAM 0x202e4fc8 max map cache */
extern const uint8_t g2_nav_msg_fields_7798a4[];                 /* ROM 0x7798a4 pb_msgdesc_t */

/* Turn icons, 60x60 lv_image_dsc_t in ROM (code 1 and the default share 0x76e264). */
extern const uint8_t g2_navigation_turn_icon_76e264[];
extern const uint8_t g2_navigation_turn_icon_76e280[];
extern const uint8_t g2_navigation_turn_icon_76e29c[];
extern const uint8_t g2_navigation_turn_icon_76e2b8[];
extern const uint8_t g2_navigation_turn_icon_76e2d4[];
extern const uint8_t g2_navigation_turn_icon_76e2f0[];
extern const uint8_t g2_navigation_turn_icon_76e30c[];
extern const uint8_t g2_navigation_turn_icon_76e328[];
extern const uint8_t g2_navigation_turn_icon_76e344[];
extern const uint8_t g2_navigation_turn_icon_76e360[];
extern const uint8_t g2_navigation_turn_icon_76e37c[];
extern const uint8_t g2_navigation_turn_icon_76e398[];
extern const uint8_t g2_navigation_turn_icon_76e3b4[];
extern const uint8_t g2_navigation_turn_icon_76e3d0[];
extern const uint8_t g2_navigation_turn_icon_76e3ec[];
extern const uint8_t g2_navigation_turn_icon_76e408[];
extern const uint8_t g2_navigation_turn_icon_76e424[];
extern const uint8_t g2_navigation_turn_icon_76e440[];
extern const uint8_t g2_navigation_turn_icon_76e45c[];
extern const uint8_t g2_navigation_turn_icon_76e478[];
extern const uint8_t g2_navigation_turn_icon_76e494[];
extern const uint8_t g2_navigation_turn_icon_76e4b0[];
extern const uint8_t g2_navigation_turn_icon_76e4cc[];
extern const uint8_t g2_navigation_turn_icon_76e4e8[];
extern const uint8_t g2_navigation_turn_icon_76e504[];
extern const uint8_t g2_navigation_turn_icon_76e520[];
extern const uint8_t g2_navigation_turn_icon_76e53c[];
extern const uint8_t g2_navigation_turn_icon_76e558[];
extern const uint8_t g2_navigation_turn_icon_76e574[];
extern const uint8_t g2_navigation_turn_icon_76e590[];
extern const uint8_t g2_navigation_turn_icon_76e5ac[];
extern const uint8_t g2_navigation_turn_icon_76e5c8[];
extern const uint8_t g2_navigation_turn_icon_76e5e4[];
extern const uint8_t g2_navigation_turn_icon_76e600[];
extern const uint8_t g2_navigation_turn_icon_76e61c[];

/* ---- callees ---- */
extern uint32_t audio_log_flags(void);                                          /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...);                              /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);      /* 0x43c0e4 */
extern void *audio_queue_copy_bytes(void *dst, const void *src, uint32_t len);  /* memcpy 0x439be4 */
extern void *audio_uart_display_area_copy_439c04(void *dst, const void *src, uint32_t len); /* 0x439c04 */
extern uint32_t g2_log_module_length(const char *text);                         /* strlen 0x44a43c */
extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);                   /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                                     /* 0x44981c */
extern void navigation_mutex_init_585ca4(void);
extern void audio_uart_pb_stream_init(g2_pb_istream_t *out, const void *buf, uint32_t size); /* pb_istream_from_buffer 0x48f49c */
extern uint32_t audio_uart_pb_decode(void *stream, const void *fields, void *dst);           /* pb_decode 0x490120 */
extern void audio_pb_ostream_from_buffer(g2_pb_ostream_t *out, void *buf, uint32_t size);   /* 0x4905f4 */
extern uint32_t audio_pb_encode(void *stream, const void *fields, const void *src);         /* pb_encode 0x490c32 */
extern uint32_t Thread_MsgPbTxByBle(uint8_t type, uint8_t command, const void *payload,
                                    uint16_t length);                           /* 0x475b14 */
extern uint8_t audio_uart_service_mode(void);                                   /* 0x45a570, 1 = master */
extern uint32_t audio_log_wake_allowed(void);                                   /* 0x443484 */
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t app);
extern uint32_t audio_uart_master_display_refresh(uint32_t app, const void *data, uint16_t len,
                                                  uint32_t flags);              /* 0x464bb2 */
extern void audio_uart_master_display_start(uint32_t app, const void *data, uint16_t len,
                                            uint32_t flags);                    /* 0x464b2e */
extern int32_t async_request_display_reflash_45aaca(uint32_t application, const void *payload,
                                                    uint32_t length, uint32_t delay);
extern void audio_uart_ring_wear_persist_48eb32(uint32_t key, uint32_t length, const void *payload);
extern int32_t navigation_send_type_8_shared(uint8_t magic, uint8_t status, uint32_t session_id,
                                              uint32_t total_size, uint32_t compress_mode,
                                              uint32_t fragment_index, uint32_t param); /* 0x586c9e */

/* ---- strings ---- */
static const char module_tag[] = "navigation.datahandler"; /* ROM 0x7798bc */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\navigation\\navigation_data_handler.c"; /* ROM 0x6e8b84 */
static const char fn_handler[] = "navigation_data_handler"; /* ROM 0x7798d4 */
static const char none_text[] = "(none)"; /* ROM 0x78dd44 */

static const char msg_len_zero[] = "navigation_data_handler: len is 0"; /* ROM 0x756cb4 */
static const char msg_len_zero_s[] = "[navigation.datahandler]navigation_data_handler: len is 0"; /* ROM 0x71654c */
static const char msg_decode_failed[] = "navigation protobuf decode failed: %s\n"; /* ROM 0x74b57c */
static const char msg_decode_failed_s[] = "[navigation.datahandler]navigation protobuf decode failed: %s\n"; /* ROM 0x70cda4 */
static const char msg_location[] = "location_name[%d] = %s,location_icon_index[%d] = %d"; /* ROM 0x72aebc */
static const char msg_location_s[] = "[navigation.datahandler]location_name[%d] = %s,location_icon_index[%d] = %d"; /* ROM 0x6f46e8 */
static const char msg_basic_info[] = "distance = %s,road_name = %s,spend_time = %s,remain_distance = %s,eta_time = %s,speed = %s,navigate_work_method = %d"; /* ROM 0x6d6650 */
static const char msg_basic_info_s[] = "[navigation.datahandler]distance = %s,road_name = %s,spend_time = %s,remain_distance = %s,eta_time = %s,speed = %s,navigate_work_method = %d"; /* ROM 0x6d3e10 */
static const char msg_mini_first_overflow[] = "first mini map fragment size overflow: %d > %d, clear cache"; /* ROM 0x716588 */
static const char msg_mini_first_overflow_s[] = "[navigation.datahandler]first mini map fragment size overflow: %d > %d, clear cache"; /* ROM 0x6e8bd8 */
static const char msg_mini_single[] = "mini map complete (single fragment), total_size=%d, compress_mode=%d"; /* ROM 0x6fb69c */
static const char msg_mini_single_s[] = "[navigation.datahandler]mini map complete (single fragment), total_size=%d, compress_mode=%d"; /* ROM 0x6dddd4 */
static const char msg_mini_first_index[] = "navigation_data_handler mini map first fragment index error, expected 0 got %d, clear cache"; /* ROM 0x6e0ca4 */
static const char msg_mini_first_index_s[] = "[navigation.datahandler]navigation_data_handler mini map first fragment index error, expected 0 got %d, clear cache"; /* ROM 0x6a11ac */
static const char msg_mini_mismatch[] = "navigation_data_handler mini map fragment mismatch, clear cache"; /* ROM 0x70cde4 */
static const char msg_mini_mismatch_s[] = "[navigation.datahandler]navigation_data_handler mini map fragment mismatch, clear cache"; /* ROM 0x6e4380 */
static const char msg_mini_session[] = "session_id=%d total_size=%d compress_mode=%d fragment_index=%d"; /* ROM 0x70ce24 */
static const char msg_mini_session_s[] = "[navigation.datahandler]session_id=%d total_size=%d compress_mode=%d fragment_index=%d"; /* ROM 0x6e43d8 */
static const char msg_mini_fragment[] = "received mini map fragment, index=%d, total_size=%d, received=%d"; /* ROM 0x703d30 */
static const char msg_mini_fragment_s[] = "[navigation.datahandler]received mini map fragment, index=%d, total_size=%d, received=%d"; /* ROM 0x6e0d00 */
static const char msg_mini_multi[] = "mini map complete (multi fragment), total_size=%d"; /* ROM 0x72aef0 */
static const char msg_mini_multi_s[] = "[navigation.datahandler]mini map complete (multi fragment), total_size=%d"; /* ROM 0x6f4734 */
static const char msg_mini_overflow[] = "over mini map raw data size, clear cache"; /* ROM 0x7402bc */
static const char msg_mini_overflow_s[] = "[navigation.datahandler]over mini map raw data size, clear cache"; /* ROM 0x703d74 */
static const char msg_max_error[] = "navigation_data_handler receive max map data error,clear cache data"; /* ROM 0x703db8 */
static const char msg_max_error_s[] = "[navigation.datahandler]navigation_data_handler receive max map data error,clear cache data"; /* ROM 0x6e0d5c */
static const char msg_max_session[] = "max_map_session_id = %d,max_map_total_size = %d,max_map_compress_mode = %d,max_map_fragment_index = %d"; /* ROM 0x6d92f4 */
static const char msg_max_session_s[] = "[navigation.datahandler]max_map_session_id = %d,max_map_total_size = %d,max_map_compress_mode = %d,max_map_fragment_index = %d"; /* ROM 0x6d56d8 */
static const char msg_max_fragment[] = "received max map data!!!!,current index = %d,total size = %d"; /* ROM 0x70ce64 */
static const char msg_max_fragment_s[] = "[navigation.datahandler]received max map data!!!!,current index = %d,total size = %d"; /* ROM 0x6e4430 */
static const char msg_max_all[] = "received all map data!!!! ,total size = %d"; /* ROM 0x7402e8 */
static const char msg_max_all_s[] = "[navigation.datahandler]received all map data!!!! ,total size = %d"; /* ROM 0x703dfc */
static const char msg_max_overflow[] = "over max map raw data size,clear cache data"; /* ROM 0x740314 */
static const char msg_max_overflow_s[] = "[navigation.datahandler]over max map raw data size,clear cache data"; /* ROM 0x703e40 */

/* Usage record written when navigation starts (ROM 0x78dd4c). */
static const g2_nav_usage_record_t nav_start_record = {4u, 2u};

/* Full record when log flag bit 1 is set, the "[navigation.datahandler]"
 * twin (name##_s) when bit 0 or bit 2 is set. */
#define NAV_LOG(level, line, cflags, name, ...)                                                   \
    do {                                                                                          \
        if ((audio_log_flags() & 2u) != 0u)                                                       \
            audio_log_extended((level), module_tag, source_file, fn_handler, (line), name,        \
                               ##__VA_ARGS__);                                                    \
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)                     \
            (void)compress_log_output((cflags), name##_s, name##_s, ##__VA_ARGS__);              \
    } while (0)

/* Encode the shared tx message and send it as PB type 1 / command 8; 0 on
 * encode failure. */
static int32_t nav_tx_encode_send(void)
{
    g2_pb_ostream_t tmp;
    g2_pb_ostream_t stream;

    audio_pb_ostream_from_buffer(&tmp, g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if (audio_pb_encode(&stream, g2_nav_msg_fields_7798a4, g2_nav_msg_shared_20358dd4) == 0u)
        return 0;
    return (int32_t)Thread_MsgPbTxByBle(NAV_PB_TYPE, NAV_PB_COMMAND, g2_nav_tx_buf_20350430,
                                        (uint16_t)stream.bytes_written);
}

/* Max map fragment acknowledgement (type 9, oneof 7). */
int32_t navigation_send_type_9_shared(uint8_t magic, uint8_t status, uint32_t session_id,
                                       uint32_t total_size, uint32_t compress_mode,
                                       uint32_t fragment_index, uint32_t param)
{
    g2_nav_pb_msg_t *msg = (g2_nav_pb_msg_t *)(void *)g2_nav_msg_shared_20358dd4;

    (void)aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    (void)aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 9u;
    msg->magic = magic;
    msg->which = 7u;
    msg->u.max_map.session_id = session_id;
    msg->u.max_map.total_size = total_size;
    msg->u.max_map.compress_mode = compress_mode;
    msg->u.max_map.fragment_index = fragment_index;
    msg->u.max_map.param_14 = param;
    msg->u.max_map.status = status;
    return nav_tx_encode_send();
}

/* Type 1, oneof 3: a single byte value. */
int32_t navigation_send_type_1_shared(uint8_t magic, uint8_t value)
{
    g2_nav_pb_msg_t *msg = (g2_nav_pb_msg_t *)(void *)g2_nav_msg_shared_20358dd4;

    (void)aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    (void)aeabi_memset_43c0e4(g2_nav_tx_buf_20350430, NAV_TX_BUF_SIZE, 0);
    msg->type = 1u;
    msg->magic = magic;
    msg->which = 3u;
    msg->u.type1.value = value;
    return nav_tx_encode_send();
}

/* Master role, wake allowed and app 8 refresh enabled: each step returns its
 * own value so the caller keeps the stock r0 of the failing test. */
static uint32_t nav_master_sync_gate(void)
{
    uint32_t ret = audio_uart_service_mode();
    if (ret != 1u)
        return ret;
    ret = audio_log_wake_allowed();
    if (ret != 1u)
        return ret;
    return audio_quicklist_refresh_enabled_4434d0(NAV_APP_ID);
}

/* Forward [cmd][magic] (6 bytes, rest of the record left as is) on refresh. */
static uint32_t nav_forward_refresh(uint8_t cmd, uint8_t magic)
{
    g2_nav_page_msg_t page;
    uint32_t ret = nav_master_sync_gate();
    if (ret == 1u) {
        page.cmd = cmd;
        page.input = magic;
        ret = audio_uart_master_display_refresh(NAV_APP_ID, &page, 6u, 0u);
    }
    return ret;
}

/* Same through the asynchronous reflash request. */
static int32_t nav_forward_reflash(uint8_t cmd, uint8_t magic, uint32_t length, uint32_t delay)
{
    g2_nav_page_msg_t page;
    int32_t ret = (int32_t)nav_master_sync_gate();
    if (ret == 1) {
        page.cmd = cmd;
        page.input = magic;
        ret = async_request_display_reflash_45aaca(NAV_APP_ID, &page, length, delay);
    }
    return ret;
}

static void nav_mini_map_publish(const g2_nav_mini_map_cache_t *cache)
{
    g2_navigation_ui_data_t *ui = &g2_navigation_ui_data_202c0d70;

    ui->mini_map_ready = 1u;
    ui->mini_map_size = cache->total_size;
    ui->mini_map_compress_mode = cache->compress_mode;
    ui->mini_map_param_198 = cache->param_10;
    ui->mini_map_param_47ec = (uint8_t)cache->param_14;
    (void)aeabi_memset_43c0e4(ui->mini_map_data, NAV_MINI_MAP_SIZE, 0);
    (void)audio_queue_copy_bytes(ui->mini_map_data, cache->data, cache->total_size);
}

static void nav_max_map_publish(const g2_nav_max_map_cache_t *cache)
{
    g2_navigation_ui_data_t *ui = &g2_navigation_ui_data_202c0d70;

    ui->max_map_ready = 1u;
    ui->max_map_compress_mode = cache->compress_mode;
    ui->max_map_size = cache->total_size;
    (void)audio_queue_copy_bytes(ui->max_map_data, cache->data, cache->total_size);
}

static int32_t nav_rx_mini_map(const g2_nav_pb_msg_t *msg, uint8_t magic)
{
    g2_nav_mini_map_cache_t *cache = (g2_nav_mini_map_cache_t *)(void *)g2_nav_buf_20329600;
    const g2_nav_pb_mini_map_t *in = &msg->u.mini_map;
    uint32_t session_id = in->session_id;
    uint32_t total_size = in->total_size;
    uint32_t compress_mode = in->compress_mode;
    uint32_t fragment_index = in->fragment_index;
    uint32_t param = in->param_2020;
    uint32_t size = in->size;

    (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
    if (cache->received == 0u && cache->fragment_index == 0u) {
        if (in->fragment_index != 0u) {
            NAV_LOG(2u, 0x393u, 0x08400000u, msg_mini_first_index, fragment_index);
            (void)navigation_send_type_8_shared(magic, NAV_STATUS_ERROR, session_id, total_size,
                                                compress_mode, fragment_index, param);
        } else {
            cache->session_id = session_id;
            cache->total_size = total_size;
            cache->compress_mode = compress_mode;
            cache->param_10 = in->param_2010;
            cache->param_14 = in->param_2014;
            cache->fragment_index = fragment_index;
            cache->param_1c = param;
            if (size > NAV_MINI_MAP_SIZE) {
                NAV_LOG(1u, 0x36cu, 0x04800000u, msg_mini_first_overflow, size, NAV_MINI_MAP_SIZE);
                (void)navigation_send_type_8_shared(magic, NAV_STATUS_ERROR, session_id, total_size,
                                                    compress_mode, fragment_index, param);
                (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
                return osMutexRelease(g2_navigation_mutex);
            }
            (void)audio_queue_copy_bytes(&cache->data[cache->received], in->bytes, size);
            cache->received += size;
            (void)navigation_send_type_8_shared(magic, NAV_STATUS_OK, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                cache->fragment_index, cache->param_1c);
            if (cache->received == total_size) {
                nav_mini_map_publish(cache);
                NAV_LOG(3u, 0x386u, 0x0c800000u, msg_mini_single, cache->total_size,
                        cache->compress_mode);
                (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
                (void)nav_forward_reflash(NAV_RX_MINI_MAP, magic, 6u, 200u);
            }
        }
    } else if (cache->session_id == session_id && cache->total_size == total_size &&
               cache->compress_mode == compress_mode && cache->fragment_index == fragment_index - 1u) {
        cache->fragment_index = fragment_index;
        if (size + cache->received <= NAV_MINI_MAP_SIZE) {
            (void)audio_queue_copy_bytes(&cache->data[cache->received], in->bytes, size);
            cache->received += size;
            (void)navigation_send_type_8_shared(magic, NAV_STATUS_OK, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                cache->fragment_index, param);
            NAV_LOG(3u, 0x3b7u, 0x0cc00000u, msg_mini_fragment, cache->fragment_index,
                    cache->total_size, cache->received);
            if (cache->received == cache->total_size) {
                NAV_LOG(3u, 0x3b9u, 0x0c400000u, msg_mini_multi, cache->total_size);
                nav_mini_map_publish(cache);
                (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
                (void)nav_forward_reflash(NAV_RX_MINI_MAP, magic, 6u, 200u);
            }
        } else {
            NAV_LOG(1u, 0x3ccu, 0x04000000u, msg_mini_overflow);
            (void)navigation_send_type_8_shared(magic, NAV_STATUS_ERROR, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                fragment_index, param);
            (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
        }
    } else {
        NAV_LOG(2u, 0x39eu, 0x08000000u, msg_mini_mismatch);
        NAV_LOG(2u, 0x3a0u, 0x09000000u, msg_mini_session, session_id, total_size, compress_mode,
                fragment_index);
        (void)navigation_send_type_8_shared(magic, NAV_STATUS_ERROR, cache->session_id,
                                            cache->total_size, cache->compress_mode,
                                            fragment_index, param);
        (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
    }
    return osMutexRelease(g2_navigation_mutex);
}

static int32_t nav_rx_max_map(const g2_nav_pb_msg_t *msg, uint8_t magic)
{
    g2_nav_max_map_cache_t *cache = (g2_nav_max_map_cache_t *)(void *)g2_nav_buf_202e4fc8;
    const g2_nav_pb_max_map_t *in = &msg->u.max_map;
    uint32_t session_id = in->session_id;
    uint32_t total_size = in->total_size;
    uint32_t compress_mode = in->compress_mode;
    uint32_t fragment_index = in->fragment_index;
    uint32_t param = in->param_14;

    (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
    if (cache->received == 0u && cache->fragment_index == 0u) {
        if (in->fragment_index != 0u) {
            NAV_LOG(2u, 0x40au, 0x08000000u, msg_max_error);
            NAV_LOG(2u, 0x40cu, 0x09000000u, msg_max_session, session_id, total_size,
                    compress_mode, fragment_index);
            (void)navigation_send_type_9_shared(magic, NAV_STATUS_ERROR, session_id, total_size,
                                                compress_mode, fragment_index, param);
        } else {
            /* No size check on the first fragment; param_14 is not cached. */
            cache->session_id = in->session_id;
            cache->total_size = in->total_size;
            cache->compress_mode = in->compress_mode;
            cache->fragment_index = in->fragment_index;
            (void)audio_queue_copy_bytes(&cache->data[cache->received], in->bytes, in->size);
            cache->received += in->size;
            (void)navigation_send_type_9_shared(magic, NAV_STATUS_OK, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                cache->fragment_index, cache->param_14);
            if (cache->received == total_size) {
                nav_max_map_publish(cache);
                (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
                (void)nav_forward_reflash(NAV_RX_MAX_MAP, magic, 6u, 200u);
            }
        }
    } else if (cache->session_id == session_id && cache->total_size == total_size &&
               cache->compress_mode == compress_mode && cache->fragment_index == fragment_index - 1u) {
        cache->fragment_index = in->fragment_index;
        if (cache->received + in->size <= NAV_MAX_MAP_SIZE) {
            (void)audio_queue_copy_bytes(&cache->data[cache->received], in->bytes, in->size);
            cache->received += in->size;
            (void)navigation_send_type_9_shared(magic, NAV_STATUS_OK, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                cache->fragment_index, param);
            NAV_LOG(3u, 0x430u, 0x0c800000u, msg_max_fragment, cache->fragment_index,
                    cache->total_size);
            if (cache->received == cache->total_size) {
                NAV_LOG(3u, 0x433u, 0x0c400000u, msg_max_all, cache->total_size);
                nav_max_map_publish(cache);
                (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
                (void)nav_forward_reflash(NAV_RX_MAX_MAP, magic, 6u, 200u);
            }
        } else {
            NAV_LOG(1u, 0x449u, 0x04000000u, msg_max_overflow);
            (void)navigation_send_type_9_shared(magic, NAV_STATUS_ERROR, cache->session_id,
                                                cache->total_size, cache->compress_mode,
                                                fragment_index, param);
            (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
        }
    } else {
        /* Stock clears the cache before building the error ack, so the
         * session / size / mode sent back are zero. */
        (void)aeabi_memset_43c0e4(cache, sizeof *cache, 0);
        NAV_LOG(2u, 0x41bu, 0x08000000u, msg_max_error);
        (void)navigation_send_type_9_shared(magic, NAV_STATUS_ERROR, cache->session_id,
                                            cache->total_size, cache->compress_mode,
                                            fragment_index, param);
    }
    return osMutexRelease(g2_navigation_mutex);
}

/* Registry data callback (via 0x585cca). Returns -1 for an empty frame, 0 for
 * a decode failure; otherwise stock leaves the last callee result in r0. */
int32_t navigation_data_dispatch(const uint8_t *data, uint32_t len)
{
    g2_nav_pb_msg_t *msg = (g2_nav_pb_msg_t *)(void *)g2_navigation_pb_rx_msg_20356db0;
    g2_pb_istream_t tmp;
    g2_pb_istream_t stream;
    g2_nav_page_msg_t page;
    int32_t ret;
    uint8_t magic;

    navigation_mutex_init_585ca4();
    if (len == 0u) {
        NAV_LOG(1u, 0x2d3u, 0x04000000u, msg_len_zero);
        return -1;
    }
    (void)aeabi_memset_43c0e4(msg, NAV_MSG_SIZE, 0);
    audio_uart_pb_stream_init(&tmp, data, len);
    (void)audio_uart_display_area_copy_439c04(&stream, &tmp, sizeof stream);
    if ((uint8_t)audio_uart_pb_decode(&stream, g2_nav_msg_fields_7798a4, msg) == 0u) {
        NAV_LOG(1u, 0x2dbu, 0x04400000u, msg_decode_failed,
                stream.errmsg != NULL ? stream.errmsg : none_text);
        return 0;
    }

    magic = msg->magic;
    ret = msg->type;
    switch (msg->type) {
    case NAV_RX_HEARTBEAT:
    case NAV_RX_NONE_LOCATION_LIST:
    case NAV_RX_RECALCULATING:
    case NAV_RX_COMPLETE:
        ret = (int32_t)nav_forward_refresh(msg->type, magic);
        break;

    case NAV_RX_LOCATION_LIST: {
        g2_navigation_location_list_t *list = &g2_navigation_location_list_20376c38;
        const g2_nav_pb_location_list_t *in = &msg->u.location_list;

        ret = msg->which;
        if (msg->which != 4u)
            break;
        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        (void)aeabi_memset_43c0e4(list, sizeof *list, 0);
        g2_nav_var_20074758 = 1u;
        list->count = in->name_count;
        for (uint32_t i = 0u; i < in->total; i++) {
            NAV_LOG(3u, 0x2f8u, 0x0d000000u, msg_location, i, in->name[i], i, in->icon_index[i]);
            (void)audio_queue_copy_bytes(list->name[i], in->name[i], g2_log_module_length(in->name[i]));
            list->icon_type[i] = in->icon_index[i];
        }
        (void)osMutexRelease(g2_navigation_mutex);
        ret = nav_forward_reflash(NAV_RX_LOCATION_LIST, magic, 2u, 500u);
        break;
    }

    case NAV_RX_START:
        ret = audio_uart_service_mode();
        if (ret == 1) {
            g2_nav_usage_record_t record;
            (void)aeabi_memset_43c0e4(&page, sizeof page, 0);
            page.cmd = NAV_RX_START;
            page.input = magic;
            audio_uart_master_display_start(NAV_APP_ID, &page, 6u, 0u);
            record = nav_start_record;
            audio_uart_ring_wear_persist_48eb32(NAV_START_RECORD_KEY, 2u, &record);
        }
        break;

    case NAV_RX_ERROR_INFO:
        ret = (int32_t)nav_master_sync_gate();
        if (ret == 1) {
            (void)aeabi_memset_43c0e4(&page, sizeof page, 0);
            page.cmd = NAV_RX_ERROR_INFO;
            page.input = magic;
            page.value[0] = (uint8_t)msg->u.error_info.value;
            ret = (int32_t)audio_uart_master_display_refresh(NAV_APP_ID, &page, 6u, 0u);
        }
        break;

    case NAV_RX_BASIC_INFO: {
        g2_navigation_info_t *info = &g2_navigation_info_staging_2037bdd0;
        const g2_nav_pb_basic_info_t *in = &msg->u.basic_info;

        (void)osMutexAcquire(g2_navigation_mutex, WAIT_FOREVER);
        (void)aeabi_memset_43c0e4(info, sizeof *info, 0);
        info->valid = 1u;
        info->field_04 = in->turn_icon;
        (void)audio_queue_copy_bytes(info->distance, in->distance, g2_log_module_length(in->distance));
        (void)audio_queue_copy_bytes(info->road_name, in->road_name, g2_log_module_length(in->road_name));
        (void)audio_queue_copy_bytes(info->spend_time, in->spend_time, g2_log_module_length(in->spend_time));
        (void)audio_queue_copy_bytes(info->remain_distance, in->remain_distance,
                                     g2_log_module_length(in->remain_distance));
        (void)audio_queue_copy_bytes(info->eta_time, in->eta_time, g2_log_module_length(in->eta_time));
        (void)audio_queue_copy_bytes(info->speed, in->speed, g2_log_module_length(in->speed));
        info->navigate_work_method = in->navigate_work_method;
        (void)osMutexRelease(g2_navigation_mutex);
        NAV_LOG(3u, 0x347u, 0x0dc00000u, msg_basic_info, info->distance, info->road_name,
                info->spend_time, info->remain_distance, info->eta_time, info->speed,
                info->navigate_work_method);
        ret = nav_forward_reflash(NAV_RX_BASIC_INFO, magic, 6u, 500u);
        break;
    }

    case NAV_RX_MINI_MAP:
        ret = nav_rx_mini_map(msg, magic);
        break;

    case NAV_RX_MAX_MAP:
        ret = nav_rx_max_map(msg, magic);
        break;

    case NAV_RX_EXIT:
        ret = (int32_t)nav_master_sync_gate();
        if (ret == 1) {
            (void)aeabi_memset_43c0e4(&page, sizeof page, 0);
            page.cmd = NAV_RX_EXIT;
            page.input = magic;
            ret = (int32_t)audio_uart_master_display_refresh(NAV_APP_ID, &page, 6u, 0u);
        }
        break;

    default:
        break;
    }
    return ret;
}

/* Turn icon for a navigation action code 1..35; 0 and unknown codes fall back
 * to the code 1 icon. */
const void *navigation_icon_name_for_code(uint32_t code)
{
    switch (code) {
    case 1u: return g2_navigation_turn_icon_76e264;
    case 2u: return g2_navigation_turn_icon_76e398;
    case 3u: return g2_navigation_turn_icon_76e4cc;
    case 4u: return g2_navigation_turn_icon_76e590;
    case 5u: return g2_navigation_turn_icon_76e5ac;
    case 6u: return g2_navigation_turn_icon_76e5c8;
    case 7u: return g2_navigation_turn_icon_76e5e4;
    case 8u: return g2_navigation_turn_icon_76e600;
    case 9u: return g2_navigation_turn_icon_76e61c;
    case 10u: return g2_navigation_turn_icon_76e280;
    case 11u: return g2_navigation_turn_icon_76e2b8;
    case 12u: return g2_navigation_turn_icon_76e2d4;
    case 13u: return g2_navigation_turn_icon_76e2f0;
    case 14u: return g2_navigation_turn_icon_76e30c;
    case 15u: return g2_navigation_turn_icon_76e328;
    case 16u: return g2_navigation_turn_icon_76e344;
    case 17u: return g2_navigation_turn_icon_76e360;
    case 18u: return g2_navigation_turn_icon_76e37c;
    case 19u: return g2_navigation_turn_icon_76e3b4;
    case 20u: return g2_navigation_turn_icon_76e3d0;
    case 21u: return g2_navigation_turn_icon_76e3ec;
    case 22u: return g2_navigation_turn_icon_76e408;
    case 23u: return g2_navigation_turn_icon_76e424;
    case 24u: return g2_navigation_turn_icon_76e440;
    case 25u: return g2_navigation_turn_icon_76e45c;
    case 26u: return g2_navigation_turn_icon_76e478;
    case 27u: return g2_navigation_turn_icon_76e494;
    case 28u: return g2_navigation_turn_icon_76e4b0;
    case 29u: return g2_navigation_turn_icon_76e4e8;
    case 30u: return g2_navigation_turn_icon_76e504;
    case 31u: return g2_navigation_turn_icon_76e520;
    case 32u: return g2_navigation_turn_icon_76e53c;
    case 33u: return g2_navigation_turn_icon_76e558;
    case 34u: return g2_navigation_turn_icon_76e574;
    case 35u: return g2_navigation_turn_icon_76e29c;
    default: return g2_navigation_turn_icon_76e264;
    }
}
