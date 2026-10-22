/* Onboarding UI storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owners app\gui\onboarding (main page, news/stock feature pages, weather/battery strip).
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

const int32_t g2_onboarding_indicator_x_78f504 = 206; /* ROM 0x78f504 */

const int32_t g2_onboarding_indicator_y0_78f508 = 114; /* ROM 0x78f508 */

const int32_t g2_onboarding_indicator_size_78f50c = 6; /* ROM 0x78f50c */

const int32_t g2_onboarding_indicator_pitch_78f510 = 16; /* ROM 0x78f510 */

int32_t g2_onboarding_scroll_duration = 390; /* RAM 0x20004284 (.data, init record 0x75d3f4) */

int32_t g2_onboarding_bounce_distance = 80; /* RAM 0x20004288 (.data, init record 0x75d3f4) */

int32_t g2_onboarding_bounce_duration = 260; /* RAM 0x2000428c (.data, init record 0x75d3f4) */

static const char weekday_key_784888[] = "ID_DASHBOARD_SUN"; /* ROM 0x784888 */
static const char weekday_key_78489c[] = "ID_DASHBOARD_MON"; /* ROM 0x78489c */
static const char weekday_key_7848b0[] = "ID_DASHBOARD_TUE"; /* ROM 0x7848b0 */
static const char weekday_key_7848c4[] = "ID_DASHBOARD_WED"; /* ROM 0x7848c4 */
static const char weekday_key_7848d8[] = "ID_DASHBOARD_THU"; /* ROM 0x7848d8 */
static const char weekday_key_7848ec[] = "ID_DASHBOARD_FRI"; /* ROM 0x7848ec */
static const char weekday_key_784900[] = "ID_DASHBOARD_SAT"; /* ROM 0x784900 */
/* RAM 0x20004294 (.data 0x20000000 init stream): Sunday-first i18n keys; RAM 0x200042b0 (= 5) is a separate cell. */
const char *g2_onboarding_weekday_keys[7] = {
    weekday_key_784888, weekday_key_78489c, weekday_key_7848b0, weekday_key_7848c4, weekday_key_7848d8, weekday_key_7848ec, weekday_key_784900,
};

int32_t g2_onboarding_indicator_count = 2; /* RAM 0x200042b4 (.data, init record 0x75d3f4) */

int32_t g2_onboarding_news_tile_index_200042b8 = -1; /* RAM 0x200042b8 (.data, init record 0x75d3f4) */

__attribute__((aligned(8))) uint8_t g2_onboarding_news_record_20061110[0xc88]; /* RAM 0x20061110; extern view: g2_onboarding_news_record_t g2_onboarding_news_record_20061110; */

__attribute__((aligned(8))) uint8_t g2_onboarding_news_reflash_record_20061d98[0xc88]; /* RAM 0x20061d98; extern view: g2_onboarding_news_record_t g2_onboarding_news_reflash_record_20061d98; */

__attribute__((aligned(4))) uint8_t g2_onboarding_stock_page_20071048[0xcc]; /* RAM 0x20071048; extern view: g2_onboarding_news_scroll_t g2_onboarding_stock_page_20071048; */

__attribute__((aligned(4))) uint8_t g2_onboarding_news_state_200715c8[0xa8]; /* RAM 0x200715c8; extern view: uint8_t g2_onboarding_news_state_200715c8[0xa8]; */

void *g2_onboarding_tile_list[12]; /* RAM 0x200734ec */

void *g2_onboarding_indicator_objs[6]; /* RAM 0x20073c68 */

__attribute__((aligned(4))) uint8_t g2_onboarding_news_pending_20073c80[0x18]; /* RAM 0x20073c80; extern view: g2_onboarding_news_pending_t g2_onboarding_news_pending_20073c80; */

void *g2_onboarding_root_obj; /* RAM 0x20074834 */

uint32_t g2_onboarding_darkened; /* RAM 0x20074838 */

void *g2_onboarding_event_fifo; /* RAM 0x20074cdc */

void *g2_onboarding_main_obj_20074ce0; /* RAM 0x20074ce0 */

int32_t g2_onboarding_feature_page_open; /* RAM 0x20074ce4 */

void *g2_onboarding_main_obj_20074ce8; /* RAM 0x20074ce8 */

void *g2_onboarding_main_obj_20074cec; /* RAM 0x20074cec */

void *g2_onboarding_main_obj_20074cf0; /* RAM 0x20074cf0 */

void *g2_onboarding_main_obj_20074cf4; /* RAM 0x20074cf4 */

void *g2_onboarding_main_obj_20074cf8; /* RAM 0x20074cf8 */

void *g2_onboarding_main_obj_20074cfc; /* RAM 0x20074cfc */

void *g2_onboarding_main_obj_20074d08; /* RAM 0x20074d08 */

void *g2_onboarding_main_obj_20074d0c; /* RAM 0x20074d0c */

void *g2_onboarding_main_obj_20074d10; /* RAM 0x20074d10 */

void *g2_onboarding_main_obj_20074d14; /* RAM 0x20074d14 */

void *g2_onboarding_main_obj_20074d18; /* RAM 0x20074d18 */

void *g2_onboarding_main_obj_20074d1c; /* RAM 0x20074d1c */

void *g2_onboarding_main_obj_20074d20; /* RAM 0x20074d20 */

void *g2_onboarding_main_obj_20074d24; /* RAM 0x20074d24 */

void *g2_onboarding_main_obj_20074d28; /* RAM 0x20074d28 */

void *g2_onboarding_main_obj_20074d2c; /* RAM 0x20074d2c */

void *g2_onboarding_main_obj_20074d30[6]; /* RAM 0x20074d30 */

void *g2_onboarding_main_obj_20074d48[6]; /* RAM 0x20074d48 */

void *g2_onboarding_main_obj_20074d60; /* RAM 0x20074d60 */

void *g2_onboarding_main_obj_20074d64; /* RAM 0x20074d64 */

void *g2_onboarding_main_obj_20074d68; /* RAM 0x20074d68 */

int32_t g2_onboarding_tile_index; /* RAM 0x20074d6c */

int32_t g2_onboarding_opened_page; /* RAM 0x20074d70 */

int32_t g2_onboarding_list_saved_y; /* RAM 0x20074d78 */

int32_t g2_onboarding_anim_busy; /* RAM 0x20074d7c */

int32_t g2_onboarding_main_flag_20074d88; /* RAM 0x20074d88 */

void *g2_onboarding_news_anim_obj_20074d8c; /* RAM 0x20074d8c */

int32_t g2_onboarding_news_shown_20074d90; /* RAM 0x20074d90 */

int32_t g2_onboarding_news_animating_20074d94; /* RAM 0x20074d94 */

void *g2_onboarding_news_widget_20074d98; /* RAM 0x20074d98 */

void *g2_onboarding_news_icon_20074d9c; /* RAM 0x20074d9c */

void *g2_onboarding_news_title_20074da0; /* RAM 0x20074da0 */

void *g2_onboarding_news_content1_20074da4; /* RAM 0x20074da4 */

void *g2_onboarding_news_content2_20074da8; /* RAM 0x20074da8 */

void *g2_onboarding_news_time_20074dac; /* RAM 0x20074dac */

void *g2_onboarding_news_ext_fifo_20074db0; /* RAM 0x20074db0 */

void *g2_onboarding_stock_obj_20074db4; /* RAM 0x20074db4 */

int32_t g2_onboarding_stock_flag_20074db8; /* RAM 0x20074db8 */

uint8_t g2_onboarding_wait_peer_ack; /* RAM 0x2007503d */

uint8_t g2_onboarding_news_anim_kind_2007503e; /* RAM 0x2007503e */

__attribute__((aligned(1))) uint8_t g2_onboarding_ble_saved[0x3]; /* RAM 0x200f47c4; extern view: g2_onboarding_ble_saved_t g2_onboarding_ble_saved; */

__attribute__((aligned(4))) uint8_t g2_onboarding_weather[0x38]; /* RAM 0x200f47c8; extern view: g2_onboarding_weather_t g2_onboarding_weather; */

__attribute__((aligned(4))) uint8_t g2_onboarding_weather_rx[0x38]; /* RAM 0x20120308; extern view: g2_onboarding_weather_t g2_onboarding_weather_rx; */

__attribute__((aligned(8))) uint8_t g2_onboarding_news_fifo_20120340[0x10]; /* RAM 0x20120340; extern view: g2_onboarding_news_fifo_t g2_onboarding_news_fifo_20120340; */
