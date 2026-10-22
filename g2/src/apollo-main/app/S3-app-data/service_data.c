/* Product protobuf services, notification thread, input / gesture / wear
 * services, transport-protocol send and UI page storage (S3
 * storage-definition pass, 2.2.6.10).
 *
 * Stock owners are named per block. .data values are from the decoded
 * startup init image (scatter record 0x75d3f4, RAM 0x20000000..0x20004557);
 * other RAM cells are zero-init (0x20004558..0x20075048 or SSRAM). ROM objects
 * are copied from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0).
 * Opaque records are aligned byte arrays sized by the referencing C type and
 * the stride to the next stock object. */
#include <stdint.h>

/* ---- a-55-pb-health / x-03-pb-health ----------------------------------- */

/* RAM 0x200f5aa8 / 0x200f5dc4 (SSRAM): health RX / TX messages, 0x31c each. */
__attribute__((aligned(4))) uint8_t g2_health_pb_rx_msg_200f5aa8[0x31c];
__attribute__((aligned(4))) uint8_t g2_health_pb_tx_msg[0x31c];
__attribute__((aligned(4))) uint8_t g2_health_pb_tx_packet[0x100]; /* RAM 0x2037c6a0 */

/* ---- a-25-pb-dev-config / pb_service_dev_setting.c ---------------------- */

/* RAM 0x200f57b4 (SSRAM): g2_devcfg_msg_t, 0xd0 bytes. */
__attribute__((aligned(4))) uint8_t g2_devcfg_tx_msg_200f57b4[0xd0];
__attribute__((aligned(4))) uint8_t g2_devcfg_tx_buffer_2037c3a0[0x100]; /* RAM 0x2037c3a0 */

typedef struct {
    uint32_t utc_second; /* +0 */
    int8_t time_zone;    /* +4 */
} g2_time_sync_info_t;
_Static_assert(sizeof(g2_time_sync_info_t) == 8u, "TIME_SYNC copy");
/* RAM 0x20004394 (.data): all zero in the init image. */
g2_time_sync_info_t g2_pb_time_sync_info_20004394 = {0u, 0};

/* ---- p-03-general-configure / service_kvdb_module_configure.c ----------- */

/* RAM 0x20000038 (.data): 0a 00 00 00, kvDashboardAutoCloseValue default 10. */
uint32_t g2_kvdb_dashboard_auto_close_value = 10u;
volatile uint32_t g2_general_configure_language_dirty;   /* RAM 0x20074604 */
volatile uint32_t g2_general_configure_auto_close_dirty; /* RAM 0x20074608 */
uint8_t g2_general_configure_tx_buffer[13];               /* RAM 0x20073e54, GC_RESPONSE_BYTES */
/* RAM 0x2037ce2c / 0x2037ce34 (SSRAM): ModuleConfigure messages, 8 bytes. */
__attribute__((aligned(4))) uint8_t g2_general_configure_rx_message[8];
__attribute__((aligned(4))) uint8_t g2_general_configure_tx_message[8];

/* ---- logger setting (logger_setting_handler.c / logger_setting_files.c) - */

/* RAM 0x203766c0 / 0x2037769c / 0x20377194 (SSRAM). */
__attribute__((aligned(4))) uint8_t g2_logger_setting_tx_encoded[0x578];
__attribute__((aligned(4))) uint8_t g2_logger_setting_rx_msg[0x508];
__attribute__((aligned(4))) uint8_t g2_logger_setting_tx_msg[0x508];
/* RAM 0x2037b098 (SSRAM): g2_logger_file_list_t, 0x328 bytes. */
__attribute__((aligned(4))) uint8_t g2_logger_file_list[0x328];
volatile int32_t g2_master_file_list_stored_flag; /* RAM 0x200746ac */

/* ---- a-12-thread-notification ------------------------------------------- */

typedef struct {
    void (*init)(void);   /* +0x00 */
    void (*deinit)(void); /* +0x04 */
    void *thread;         /* +0x08 */
    void *queue;          /* +0x0c */
    uint32_t reserved[5]; /* +0x10 */
} g2_notif_thread_record_t;
_Static_assert(sizeof(g2_notif_thread_record_t) == 0x24u, "thread context stride");

extern void thread_notification_create(void);  /* 0x48e212 */
extern void thread_notification_destroy(void); /* 0x48e242 */

/* RAM 0x200040fc (.data): {0x48e213, 0x48e243, 0...}, thread-manager slot 1. */
g2_notif_thread_record_t g2_notif_thread_context = {
    thread_notification_create, thread_notification_destroy, 0, 0, {0u, 0u, 0u, 0u, 0u}};
__attribute__((aligned(8))) uint8_t g2_notif_thread_cb[0x70];      /* RAM 0x20072450, static TCB */
__attribute__((aligned(8))) uint8_t g2_notif_thread_stack[0x2000]; /* RAM 0x20362e18 (SSRAM) */

/* ---- service_input_manager.c -------------------------------------------- */

/* RAM 0x200036f8 (.data): ff ff 00 00, no current device type. */
uint32_t g2_inpm_current_dev_type = 0x0000ffffu;
uint32_t g2_inpm_tp_press_tick[3];   /* RAM 0x20074098 */
uint32_t g2_inpm_tp_release_tick[3]; /* RAM 0x200740a4 */
uint32_t g2_inpm_left_press_tick;    /* RAM 0x2007497c */
uint32_t g2_inpm_right_press_tick;   /* RAM 0x20074980 */
uint32_t g2_inpm_last_inject_tick;   /* RAM 0x20074984 */

/* ---- a-40-gesture-processor / at_tp.c ----------------------------------- */

/* RAM 0x200036ec (.data): proximity state names, ROM strings 0x788970,
 * 0x783230, 0x788980. The array object itself is RAM. */
const char *g2_touch_prox_names[3] = {"PROXIMITY_NONE", "PROXIMITY_UNWEAR", "PROXIMITY_WEAR"};
char g2_gesture_slider_text[0x60];          /* RAM 0x20072790, SLIDER_TEXT_SIZE */
volatile uint8_t g2_touch_stream_enabled;   /* RAM 0x20075017 */
volatile uint8_t g2_touch_prox_state;       /* RAM 0x20075018 */

/* ---- a-16-wear-detect: wear_detect_sync.c ------------------------------- */

typedef struct {
    uint8_t type;   /* +0 */
    uint8_t pad[3]; /* +1 */
    uint32_t value; /* +4 */
} g2_wear_sync_template_t;
_Static_assert(sizeof(g2_wear_sync_template_t) == 8u, "wear sync message");

volatile uint32_t g2_wear_detect_role2_state_20074ee0; /* RAM 0x20074ee0 */
volatile uint32_t g2_wear_detect_role1_state_20074ee4; /* RAM 0x20074ee4 */
volatile uint32_t g2_wear_detect_worn_tick_20074ee8;   /* RAM 0x20074ee8 */
/* ROM 0x78ee04: 8 zero bytes. */
const g2_wear_sync_template_t g2_wear_sync_msg_template = {0u, {0u, 0u, 0u}, 0u};

/* ---- a-20-tpl-send: transport_protocol_send.c --------------------------- */

typedef struct {
    uint8_t magic, ids, sequence, frame_length, frame_count, frame_index, command, flags;
} g2_tpl_header_template_t;
_Static_assert(sizeof(g2_tpl_header_template_t) == 8u, "TPL header");
/* ROM 0x78ec74: aa 02 00 00 00 00 00 00 (magic 0xaa, sourceID 2). */
const g2_tpl_header_template_t g2_tpl_header_template = {0xaau, 0x02u, 0u, 0u, 0u, 0u, 0u, 0u};
uint8_t g2_tpl_send_payload_buffer[0x1000]; /* RAM 0x2036fe40, TPL_STATIC_BUFFER_SIZE */
uint8_t g2_tpl_send_frame_buffer[0x101];    /* RAM 0x2037c080, TPL_FRAME_BUFFER_SIZE */

/* ---- uart_sync_receive.c ------------------------------------------------ */

uint8_t g2_uart_sync_rx_buffer[0x400]; /* RAM 0x2037a1a0, UART_SYNC_RX_BUFFER_SIZE */
uint32_t g2_uart_sync_rx_length;       /* RAM 0x20074614 */

/* ---- onboarding (onboarding.c / onboarding_data_manager.c) -------------- */

void *g2_onboarding_mutex;                  /* RAM 0x20074830 osMutexId_t */
volatile uint32_t g2_onboarding_flag_dirty; /* RAM 0x20074840 */
/* RAM 0x200f4800 (SSRAM): onboarding process head, 8 bytes (stride 8). */
__attribute__((aligned(4))) uint8_t g2_onboarding_process[8];

/* ---- a-28-even-ai-page / service_even_ai.c ------------------------------ */

void *g2_even_ai_page;                /* RAM 0x2007457c */
uint32_t g2_even_ai_last_wakeup_tick; /* RAM 0x20074978 */
void *g2_even_ai_event_fifo;          /* RAM 0x20074c00 */
uint8_t g2_even_ai_anim_busy;         /* RAM 0x2007503a */

/* ---- a-28-message-notify ------------------------------------------------ */

void *g2_msg_notif_page;            /* RAM 0x20074710 */
uint8_t g2_msg_notif_page_state[3]; /* RAM 0x20074714 {phase, reserved, timer_armed} */
void *g2_msg_notif_event_fifo;      /* RAM 0x20074cd8 */
uint8_t g2_msg_notif_anim_busy;     /* RAM 0x2007503c */

/* ---- a-11-system-close / a-24-system-alert ------------------------------ */

/* RAM 0x20071840: {data[0x80], u16 write, u16 read, u16 count}. */
__attribute__((aligned(4))) uint8_t g2_system_close_fifo[0x86];
/* RAM 0x20003bec (.data): 02, two options. */
int32_t g2_system_close_item_count = 2;
void *g2_system_close_panel;           /* RAM 0x200749fc */
void *g2_system_close_container;       /* RAM 0x20074a00 */
void *g2_system_close_arrow;           /* RAM 0x20074a08 */
void *g2_system_close_option0;         /* RAM 0x20074a0c */
void *g2_system_close_option2;         /* RAM 0x20074a10 */
void *g2_system_close_option1;         /* RAM 0x20074a14 */
int32_t g2_system_close_selected_index; /* RAM 0x20074a18 */
void *g2_system_close_title;           /* RAM 0x20074a1c */
uint8_t g2_system_close_popup_shown;   /* RAM 0x20075027 */
uint8_t g2_system_close_anim_busy;     /* RAM 0x20075028 */
uint32_t g2_system_alert_ring_event_tick; /* RAM 0x200749f8 */

/* ---- a-11-silent-mode --------------------------------------------------- */

/* RAM 0x20073ae4: g2_silent_mode_ui_t, 0x1c bytes. */
__attribute__((aligned(4))) uint8_t g2_silent_mode_ui[0x1c];
void *g2_silent_mode_root_page; /* RAM 0x200749c0 */
