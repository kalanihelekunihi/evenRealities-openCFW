/* Dashboard / news / stock / schedule / page-state storage (S3
 * storage-definition pass, 2.2.6.10).
 *
 * Stock owners: the dashboard app (a-16-dashboard handlers and async update),
 * dashboard_data_process.c (a-38, protobuf package and stock bitmaps), the
 * package parser (x-01-dashboard-parse), the dashboard extension protobuf file
 * (a-39-dashboard-ext), page-state sync (a-39-page-state-sync) and the
 * quicklist notify event. .data values are from the decoded startup init
 * image (scatter record 0x75d3f4, RAM 0x20000000..0x20004557); all other
 * cells are zero-init (0x20004558..0x20075048 or SSRAM). Opaque records are
 * aligned byte arrays sized by the referencing C type (sizeof in the
 * referencing unit) and the stride to the next stock object.
 *
 * ui/a-15-dashboard names several of these cells differently
 * (g2_dashboard_mutex, g2_dashboard_calendar_events, g2_dashboard_calendar_data_b,
 * g2_dashboard_stock_data_c); those are defsym aliases owned by the ui-a pass. */
#include <stdint.h>

/* ---- a-16-dashboard: dashboard_handlers.c ------------------------------- */

volatile uint32_t g2_dashboard_widgets_darkened_200743b4; /* RAM 0x200743b4 */
void *volatile g2_dashboard_root_200743b8;                /* RAM 0x200743b8 lv_obj_t * */
volatile uint32_t g2_dashboard_last_hour_200743bc;        /* RAM 0x200743bc */
volatile uint32_t g2_dashboard_last_minute_200743c0;      /* RAM 0x200743c0 */
volatile uint32_t g2_dashboard_last_month_200743c4;       /* RAM 0x200743c4 */
volatile uint32_t g2_dashboard_last_day_200743c8;         /* RAM 0x200743c8 */
volatile uint32_t g2_dashboard_last_weekday_200743cc;     /* RAM 0x200743cc */
volatile uint32_t g2_dashboard_auto_close_enabled_200743d8; /* RAM 0x200743d8 */
volatile uint32_t g2_dashboard_auto_close_hold_20074ba0;  /* RAM 0x20074ba0 */
volatile uint8_t g2_dashboard_auto_close_fired_20074fa3;  /* RAM 0x20074fa3 */
volatile uint8_t g2_dashboard_backgrounded_20074fa4;      /* RAM 0x20074fa4 */
/* RAM 0x20132f74 (SSRAM): five news records, 0x8ef8 bytes. */
__attribute__((aligned(4))) uint8_t g2_dashboard_news_cache_20132f74[0x8ef8];
/* RAM 0x20366718 (SSRAM): parsed package, PARSED_SIZE 0x14c0
 * (x-01-dashboard-parse clears 0x14c0 bytes). */
__attribute__((aligned(4))) uint8_t g2_dashboard_parsed_data_20366718[0x14c0];

/* ---- a-16-dashboard: dashboard_async_update_data.c ---------------------- */

void *g2_dashboard_mutex_200743a8;                   /* RAM 0x200743a8 osMutexId_t */
volatile uint32_t g2_dashboard_stock_received_200743ac; /* RAM 0x200743ac */
volatile uint32_t g2_dashboard_stock_total_200743b0; /* RAM 0x200743b0 */
/* RAM 0x200e3e80 (SSRAM): settings / weather block, 0xa0 bytes (stride to
 * the event buffer). */
__attribute__((aligned(4))) uint8_t g2_dashboard_state[0xa0];
__attribute__((aligned(4))) uint8_t g2_dashboard_event_buffer_200e3f20[0x1000]; /* RAM 0x200e3f20 */
/* RAM 0x200e67f8 (SSRAM): schedule staging copy, {u16 count, pad, 8 x
 * 0x210-byte records, u32 tail} = 0x1088 bytes (stride 0x1088). */
__attribute__((aligned(4))) uint8_t g2_dashboard_schedule_staging_200e67f8[0x1088];
/* RAM 0x2011df34 (SSRAM): calendar UI copy, g2_schedule_ui_t (0x1088 bytes,
 * ui/a-32-calendar-page). Its +0x1084 member, the calendar authority word,
 * is referenced as its own symbol (RAM 0x2011efb8) and is an assembler alias
 * into this object. */
__attribute__((aligned(4))) uint8_t g2_dashboard_schedule_ui_2011df34[0x1088];
__asm__(".globl g2_dashboard_schedule_authority_2011efb8\n"
        ".set g2_dashboard_schedule_authority_2011efb8, g2_dashboard_schedule_ui_2011df34 + 0x1084\n"
        ".type g2_dashboard_schedule_authority_2011efb8, %object\n"
        ".size g2_dashboard_schedule_authority_2011efb8, 4\n");
/* RAM 0x20378974 (SSRAM): stock UI copy, 0x428 bytes
 * (dashboard_clear_stock_ui_data 0x49c668 zeroes 0x428; the async-update
 * extern declares 0x424). */
__attribute__((aligned(4))) uint8_t g2_dashboard_stock_ui_20378974[0x428];

/* ---- a-38-dashboard-data-process ---------------------------------------- */

/* RAM 0x200566c8: decoded DashboardDataPackage, g2_dashboard_package_t
 * (0xd00 bytes). */
__attribute__((aligned(4))) uint8_t g2_dashboard_package[0xd00];
__attribute__((aligned(4))) uint8_t g2_dashboard_tx_buffer[0x100]; /* RAM 0x200702ec, PB_TX_SIZE */
uint32_t g2_dashboard_last_command_id; /* RAM 0x20074408 */
uint32_t g2_dashboard_last_magic;      /* RAM 0x2007440c */
uint32_t g2_dashboard_settings_id;     /* RAM 0x20074410 */
uint8_t *g2_dashboard_payload_ptr;     /* RAM 0x20074414 */
uint8_t *g2_dashboard_settings_src;    /* RAM 0x20074418 */
uint8_t *g2_dashboard_settings_dst;    /* RAM 0x2007441c */
uint8_t *g2_dashboard_widget_ptr;      /* RAM 0x20074420 */
uint8_t *g2_dashboard_weather_ptr;     /* RAM 0x20074424 */
uint8_t *g2_dashboard_widget_data_ptr; /* RAM 0x20074428 */
uint8_t *g2_dashboard_word_ptr;        /* RAM 0x2007442c */
/* RAM 0x203024a4 (SSRAM): news staging copy, 0x8f48 bytes. */
__attribute__((aligned(4))) uint8_t g2_news_staging_203024a4[0x8f48];

/* dashboard_data_process_stock.c: nine 0x1ff8-byte stock chart bitmaps
 * (RAM 0x200bac20 + n * 0x1ff8) and the per-chart scale. */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_0[0x1ff8]; /* RAM 0x200bac20 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_1[0x1ff8]; /* RAM 0x200bcc18 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_2[0x1ff8]; /* RAM 0x200bec10 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_3[0x1ff8]; /* RAM 0x200c0c08 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_4[0x1ff8]; /* RAM 0x200c2c00 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_5[0x1ff8]; /* RAM 0x200c4bf8 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_6[0x1ff8]; /* RAM 0x200c6bf0 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_7[0x1ff8]; /* RAM 0x200c8be8 */
__attribute__((aligned(4))) uint8_t g2_stock_bmp_8[0x1ff8]; /* RAM 0x200cabe0 */
float g2_stock_chart_low[9];   /* RAM 0x20073828, STOCK_CHART_COUNT */
float g2_stock_chart_scale[9]; /* RAM 0x2007384c, STOCK_CHART_COUNT */

/* ---- x-01-dashboard-parse ----------------------------------------------- */

const uint8_t *g2_dashboard_weather_src_200743dc;    /* RAM 0x200743dc */
uint32_t g2_dashboard_news_index_base_200743e0;      /* RAM 0x200743e0 */
const uint8_t *g2_dashboard_news_src_200743e4;       /* RAM 0x200743e4 */
const uint8_t *g2_dashboard_news_item_src_200743e8;  /* RAM 0x200743e8 */
uint8_t *g2_dashboard_news_dst_200743ec;             /* RAM 0x200743ec */
const uint8_t *g2_dashboard_stock_src_200743f0;      /* RAM 0x200743f0 */
const uint8_t *g2_dashboard_stock_item_src_200743f4; /* RAM 0x200743f4 */
uint8_t *g2_dashboard_stock_dst_200743f8;            /* RAM 0x200743f8 */
const uint8_t *g2_dashboard_sched_src_200743fc;      /* RAM 0x200743fc */
const uint8_t *g2_dashboard_sched_item_src_20074400; /* RAM 0x20074400 */
uint8_t *g2_dashboard_sched_dst_20074404;            /* RAM 0x20074404 */
/* RAM 0x200005d8 (.data): ffffffff, no news index yet. */
uint32_t g2_dashboard_news_index_200005d8 = 0xffffffffu;

/* ---- a-39-dashboard-ext: dashboard_ext_pb_file.c ------------------------ */

/* RAM 0x2031f5e4 (SSRAM): g2_dash_ext_recv_t, 0x501c bytes. */
__attribute__((aligned(4))) uint8_t g2_dash_ext_recv[0x501c];
/* RAM 0x20369e1c (SSRAM): g2_dash_ext_tx_msg_t, 0x1024 bytes. */
__attribute__((aligned(4))) uint8_t g2_dash_ext_tx_msg[0x1024];
__attribute__((aligned(4))) uint8_t g2_dash_ext_tx_buffer[0x400]; /* RAM 0x2037919c */
uint32_t g2_dash_ext_upgrade_magic;                               /* RAM 0x20074430 */

/* ---- a-39-page-state-sync ----------------------------------------------- */

/* RAM 0x200732ac: g2_page_state_t, 0x3c bytes. */
__attribute__((aligned(4))) uint8_t g2_page_state[0x3c];
/* RAM 0x20074bb4 g2_dashboard_last_saved_tile is defined by the ui-a pass as
 * g2_dashboard_saved_tile_index_20074bb4 (defsym alias). */
/* RAM 0x20003060 (.data): e8 03 00 00. */
uint32_t g2_page_state_package_id = 1000u;

/* ---- quicklist notify event --------------------------------------------- */

volatile uint8_t g2_quicklist_notify_seq; /* RAM 0x20074ffd */
