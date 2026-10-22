/* Teleprompt and translate service / UI storage (S3 storage-definition pass,
 * 2.2.6.10).
 *
 * Stock owners: the teleprompt controller, timer manager, UI and protobuf
 * service (a-61-teleprompt, a-61-pb-teleprompt, ui/a-54-teleprompt-ui) and the
 * translate service, FSM, data and UI (p-10..p-14 translate,
 * pb_service_translate.c). .data values are from the decoded startup init
 * image (scatter record 0x75d3f4, RAM 0x20000000..0x20004557); other RAM
 * cells are zero-init (0x20004558..0x20075048 or SSRAM). ROM objects are
 * copied from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0).
 * Several translate cells have two names in g2/src; one is defined here and
 * the other is a defsym alias (see the S3 manifest). */
#include <stdint.h>

/* ---- a-61-teleprompt ---------------------------------------------------- */

typedef struct {
    const char *name;
    uint32_t attr_bits;
    void *cb_mem;
    uint32_t cb_size;
} g2_tp_mutex_attr_t;
_Static_assert(sizeof(g2_tp_mutex_attr_t) == 16u, "osMutexAttr_t");
/* ROM 0x7896e0: {"TelepromptActionMutex" (ROM 0x77c2a4), 0, 0, 0}. */
const g2_tp_mutex_attr_t g2_teleprompt_action_mutex_attr_7896e0 = {"TelepromptActionMutex", 0u, 0, 0u};

uint32_t g2_teleprompt_start_tick_20074a60;     /* RAM 0x20074a60 */
uint32_t g2_teleprompt_heartbeat_tick_20074a64; /* RAM 0x20074a64 */
void *g2_teleprompt_action_mutex_20074a68;      /* RAM 0x20074a68 osMutexId_t */
void *g2_teleprompt_root_20074a7c;              /* RAM 0x20074a7c */
uint8_t g2_teleprompt_rx_result_2010938c;       /* RAM 0x2010938c */
/* RAM 0x20060154 (SSRAM): decoded RX message, 0xf58 bytes. */
__attribute__((aligned(4))) uint8_t g2_teleprompt_pb_rx_msg_20060154[0xf58];

/* teleprompt_timer_mgr.c */
typedef struct {
    void (*start)(void);
    void (*stop)(void);
} g2_tp_timer_ops_t;
typedef struct {
    uint8_t from, to, timer_type, action;
} g2_tp_timer_rule_t;

extern void teleprompt_timer_countdown_start_588d74(void);   /* 0x588d74 */
extern void teleprompt_timer_countdown_stop_588df4(void);    /* 0x588df4 */
extern void teleprompt_timer_auto_scroll_start_588e42(void); /* 0x588e42 */
extern void teleprompt_timer_auto_scroll_stop_588ecc(void);  /* 0x588ecc */

/* ROM 0x77c52c: {0, 0}, {0x588d75, 0x588df5}, {0x588e43, 0x588ecd}. */
const g2_tp_timer_ops_t g2_teleprompt_timer_ops_77c52c[3] = {
    {0, 0},
    {teleprompt_timer_countdown_start_588d74, teleprompt_timer_countdown_stop_588df4},
    {teleprompt_timer_auto_scroll_start_588e42, teleprompt_timer_auto_scroll_stop_588ecc},
};
/* ROM 0x783ec4: 00 02 01 01 | 01 02 01 01 | 02 02 02 01 | 04 03 01 02 |
 * 04 03 02 02. */
const g2_tp_timer_rule_t g2_teleprompt_timer_rules_783ec4[5] = {
    {0u, 2u, 1u, 1u}, {1u, 2u, 1u, 1u}, {2u, 2u, 2u, 1u}, {4u, 3u, 1u, 2u}, {4u, 3u, 2u, 2u},
};
uint32_t g2_teleprompt_countdown_deadline_20074a74;   /* RAM 0x20074a74 */
uint32_t g2_teleprompt_auto_scroll_deadline_20074a78; /* RAM 0x20074a78 */
uint8_t g2_teleprompt_auto_scroll_running_20075029;   /* RAM 0x20075029 */
uint8_t g2_teleprompt_countdown_done_2007502a;        /* RAM 0x2007502a */
uint8_t g2_teleprompt_countdown_running_2007502b;     /* RAM 0x2007502b */
/* RAM 0x20073068: teleprompt UI window record. The referencing units
 * declare 0x40..0x48-byte views; the stock stride is 0x48. */
__attribute__((aligned(4))) uint8_t g2_teleprompt_ui_window[0x48];

/* pb_service_teleprompt.c */
uint32_t g2_teleprompt_pb_last_tick_20074870;  /* RAM 0x20074870 */
uint8_t g2_teleprompt_pb_last_magic_20074ffe;  /* RAM 0x20074ffe */
/* RAM 0x200f873c (SSRAM): TX message, 0xf58 bytes. */
__attribute__((aligned(4))) uint8_t g2_teleprompt_pb_tx_msg_200f873c[0xf58];
uint8_t g2_teleprompt_pb_tx_packet_2037c9a0[0x100]; /* RAM 0x2037c9a0, TP_PACKET_SIZE */

/* ---- translate service (translate.c / translate_data.c / translate_fsm.c) */

uint32_t g2_translate_display_start_tick; /* RAM 0x20074ae8 */
uint32_t g2_translate_heartbeat_tick;     /* RAM 0x20074aec */
void *g2_translate_action_mutex;          /* RAM 0x20074af0 osMutexId_t */
uint32_t g2_translate_src_display_len;    /* RAM 0x20074af4 */
uint32_t g2_translate_dst_display_len;    /* RAM 0x20074af8 */
/* RAM 0x20074afc: translate root page object (alias g2_translate_root_object). */
void *g2_translate_root_page;
uint8_t g2_translate_segment_ended;       /* RAM 0x20075039 */
/* RAM 0x2006496c (SSRAM): decoded RX message, 0x854 bytes. */
__attribute__((aligned(4))) uint8_t g2_translate_pb_rx_msg[0x854];
uint8_t g2_translate_pb_status; /* RAM 0x20119efc */
/* RAM 0x20119f00 (SSRAM): text ring, 0x2012 bytes (alias
 * g2_translate_text_buffer). */
__attribute__((aligned(4))) uint8_t g2_translate_text_ring[0x2012];
/* RAM 0x2011bf14 / 0x2011cf1c (SSRAM): source / target display text, 0x1008
 * each (aliases g2_translate_source_buffer / g2_translate_target_buffer). */
__attribute__((aligned(4))) char g2_translate_src_display[0x1008];
__attribute__((aligned(4))) char g2_translate_dst_display[0x1008];
/* RAM 0x2011df24 (SSRAM): translate session context, 16 bytes. The language
 * pair text the UI shows starts at +1 (RAM 0x2011df25) and is an assembler
 * alias into this object. */
__attribute__((aligned(4))) uint8_t g2_translate_session[16];
__asm__(".globl g2_translate_lang_pair_text\n"
        ".set g2_translate_lang_pair_text, g2_translate_session + 1\n"
        ".type g2_translate_lang_pair_text, %object\n"
        ".size g2_translate_lang_pair_text, 15\n");

/* RAM 0x200041a8 (.data): FSM event names, TRANSLATE_EVENT_COUNT (7) plus
 * the stock _NUM entry; ROM strings 0x77cf7c 0x77cf94 0x77cfac 0x77cfc4
 * 0x77cfdc 0x75bf40 0x773b18 0x784554. */
const char *g2_translate_event_names[8] = {
    "TRANSLATE_EVENT_NONE", "TRANSLATE_EVENT_START", "TRANSLATE_EVENT_PAUSE",
    "TRANSLATE_EVENT_RESUME", "TRANSLATE_EVENT_CLOSE", "TRANSLATE_EVENT_TRANSLATE_RESULT",
    "TRANSLATE_EVENT_HEARTBEAT", "TRANSLATE_EVENT_NUM",
};

/* ---- translate_ui.c ----------------------------------------------------- */

/* RAM 0x20073784: translate_ui_ctx_t, 0x2c bytes. */
__attribute__((aligned(4))) uint8_t g2_translate_ui_ctx[0x2c];
/* RAM 0x200041c8 (.data): UI state names, TRANSLATE_UI_STATE_NUM (3) plus the
 * _NUM entry; ROM 0x773bdc 0x773bf8 0x773c14 0x77d03c. */
const char *g2_translate_ui_state_names[4] = {
    "TRANSLATE_UI_STATE_CLOSED", "TRANSLATE_UI_STATE_RUNNING", "TRANSLATE_UI_STATE_CLOSING",
    "TRANSLATE_UI_STATE_NUM",
};
/* RAM 0x200041d8 (.data): UI event names, TRANSLATE_UI_EVENT_NUM (10) plus
 * the _NUM entry; ROM 0x77d054 0x767070 0x767090 0x7670b0 0x7670d0 0x773c30
 * 0x773c4c 0x7670f0 0x773c68 0x767110 0x77d06c. */
const char *g2_translate_ui_event_names[11] = {
    "TRANSLATE_UI_EVENT_NONE", "TRANSLATE_UI_EVENT_MODE_CHANGE",
    "TRANSLATE_UI_EVENT_TEXT_UPDATE", "TRANSLATE_UI_EVENT_MENU_START",
    "TRANSLATE_UI_EVENT_APP_START", "TRANSLATE_UI_EVENT_PAUSE", "TRANSLATE_UI_EVENT_RESUME",
    "TRANSLATE_UI_EVENT_MENU_EXIT", "TRANSLATE_UI_EVENT_APP_EXIT",
    "TRANSLATE_UI_EVENT_GIF_COMPLETE", "TRANSLATE_UI_EVENT_NUM",
};

/* ---- pb_service_translate.c --------------------------------------------- */

uint32_t g2_translate_pb_last_rx_tick; /* RAM 0x20074878 */
uint8_t g2_translate_pb_last_magic;    /* RAM 0x20075000 */
/* RAM 0x200f9ee4 (SSRAM): TX message, 0x854 bytes. */
__attribute__((aligned(4))) uint8_t g2_translate_pb_tx_msg[0x854];
uint8_t g2_translate_pb_tx_buffer[0x100]; /* RAM 0x2037caa0 */
