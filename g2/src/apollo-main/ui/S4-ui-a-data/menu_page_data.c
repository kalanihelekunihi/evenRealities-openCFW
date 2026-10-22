/* Menu page storage (S4-ui-a storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner app\gui\menu\menu_page.c (log tag "menu.page").
 * .data values come from the decoded scatter init streams (records 0x75d3f4
 * for 0x20000000.. and 0x75d404 for 0x20080000..); every other RAM cell is
 * zero-initialised (.bss 0x20004558.. / 0x2013be70..). ROM bytes are copied
 * from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0). Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. */
#include <stdint.h>

extern const struct g2_icon_descriptor g2_img_dsc_76e7dc;
extern const struct g2_icon_descriptor g2_img_dsc_76a24c;
extern const struct g2_icon_descriptor g2_img_dsc_772960;
extern const struct g2_icon_descriptor g2_img_dsc_773a00;
extern const struct g2_icon_descriptor g2_img_dsc_76e638;
extern const struct g2_icon_descriptor g2_img_dsc_76b6f8;
extern const struct g2_icon_descriptor g2_img_dsc_76a94c;
extern const struct g2_icon_descriptor g2_img_dsc_771dac;
/* ROM 0x6c2198: eight built-in menu rows {icon, i18n key, action id, app_type,
 * icon_num, app_id}; extern view g2_menu_page_item_t[8] (0x34 bytes each). */
const struct {
    const void *icon;
    char text[32];
    uint32_t text_res;
    uint8_t app_type;
    uint8_t reserved[3];
    int32_t icon_num;
    int32_t app_id;
} g2_menu_builtin_apps[8] = {
    {&g2_img_dsc_76e7dc, "ID_MENU_NOTIFICATIONS", 1u, 0u, {0u, 0u, 0u}, 0, 4},
    {&g2_img_dsc_76a24c, "ID_MENU_CONVERSATE", 2u, 0u, {0u, 0u, 0u}, 0, 11},
    {&g2_img_dsc_772960, "ID_MENU_TELEPROMPT", 3u, 0u, {0u, 0u, 0u}, 0, 6},
    {&g2_img_dsc_773a00, "ID_MENU_TRANSLATE", 4u, 0u, {0u, 0u, 0u}, 0, 5},
    {&g2_img_dsc_76e638, "ID_MENU_NAVIGATE", 5u, 0u, {0u, 0u, 0u}, 0, 8},
    {&g2_img_dsc_76b6f8, "ID_MENU_EVEN_AI", 6u, 0u, {0u, 0u, 0u}, 0, 7},
    {&g2_img_dsc_76a94c, "ID_MENU_DASHBOARD", 7u, 0u, {0u, 0u, 0u}, 0, 1},
    {&g2_img_dsc_771dac, "ID_MENU_SILENT_MODE", 8u, 0u, {0u, 0u, 0u}, 0, 266},
};

struct pb_msgdesc_candidate {
    const uint32_t *field_info;
    const struct pb_msgdesc_candidate *const *submsg_info;
    const uint8_t *default_value;
    void *field_callback;
    uint16_t field_count, required_field_count, largest_tag;
};
_Static_assert(sizeof(struct pb_msgdesc_candidate) == 24u, "ARM nanopb 0.4 pb_msgdesc_t");
/* ROM 0x779694: menu-page nanopb message graph (4 descriptors; field words,
 * submessage tables and counts copied from ROM; no defaults/callbacks).
 * extern view const uint8_t[]. */
static const struct pb_msgdesc_candidate pb_desc_779664;
static const struct pb_msgdesc_candidate pb_desc_77964c;
static const struct pb_msgdesc_candidate pb_desc_77967c;
static const uint32_t pb_fields_756978[] = { /* ROM 0x756978 */
    0x00011205u, 0x00010000u,
    0x00011209u, 0x00010001u,
    0x2001380du, 0x03780004u,
    0x20013811u, 0x00040004u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78b5ac[] = { /* ROM 0x78b5ac */
    &pb_desc_779664, &pb_desc_77967c, 0
};
const struct pb_msgdesc_candidate g2_menu_pb_msgdesc = { /* ROM 0x779694 */
    pb_fields_756978, pb_submsgs_78b5ac, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_78123c[] = { /* ROM 0x78123c */
    0x00011205u, 0x00040000u,
    0x40142809u, 0x002c0008u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78dcac[] = { /* ROM 0x78dcac */
    &pb_desc_77964c, 0
};
static const struct pb_msgdesc_candidate pb_desc_779664 = { /* ROM 0x779664 */
    pb_fields_78123c, pb_submsgs_78dcac, 0, 0, 2u, 0u, 2u
};
static const uint32_t pb_fields_779634[] = { /* ROM 0x779634 */
    0x40001204u,
    0x40041208u,
    0x0001170du, 0x00200008u,
    0x40281210u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f2c0[] = { /* ROM 0x78f2c0 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77964c = { /* ROM 0x77964c */
    pb_fields_779634, pb_submsgs_78f2c0, 0, 0, 4u, 0u, 4u
};
static const uint32_t pb_fields_78dcb4[] = { /* ROM 0x78dcb4 */
    0x40001204u,
    0u
};
static const struct pb_msgdesc_candidate *const pb_submsgs_78f2c4[] = { /* ROM 0x78f2c4 */
    0
};
static const struct pb_msgdesc_candidate pb_desc_77967c = { /* ROM 0x77967c */
    pb_fields_78dcb4, pb_submsgs_78f2c4, 0, 0, 1u, 0u, 1u
};

const int32_t g2_menu_item_height = 50; /* ROM 0x78f2c8 */

__attribute__((aligned(4))) uint8_t g2_menu_display_items[0x410]; /* RAM 0x2006a8fc; extern view: g2_menu_page_item_t g2_menu_display_items[MENU_ITEM_MAX]; */

__attribute__((aligned(4))) uint8_t g2_menu_event_fifo[0x106]; /* RAM 0x2006ffd8; extern view: g2_menu_event_fifo_t g2_menu_event_fifo; */

void *g2_menu_item_objs[20]; /* RAM 0x20072c18 */

int32_t g2_menu_configure_dirty; /* RAM 0x200746e8 */

void *g2_menu_focus_anim_obj; /* RAM 0x200746ec */

void *g2_menu_frame_obj; /* RAM 0x200746f0 */

void *g2_menu_list_obj; /* RAM 0x200746f4 */

void *g2_menu_content_container; /* RAM 0x200746f8 */

int32_t g2_menu_item_count; /* RAM 0x20074704 */

int32_t g2_menu_current_index; /* RAM 0x20074708 */

int32_t g2_menu_scroll_offset; /* RAM 0x2007470c */

volatile uint8_t g2_menu_anim_in_progress; /* RAM 0x20074fe4 */

__attribute__((aligned(4))) uint8_t g2_menu_encode_buffer[0x432]; /* RAM 0x20378540; extern view: uint8_t g2_menu_encode_buffer[0x432]; */

__attribute__((aligned(4))) uint8_t g2_menu_decode_msg[0x37c]; /* RAM 0x2037a9a0; extern view: g2_menu_pb_msg_t g2_menu_decode_msg; */

__attribute__((aligned(4))) uint8_t g2_menu_response_msg[0x37c]; /* RAM 0x2037ad1c; extern view: g2_menu_pb_msg_t g2_menu_response_msg; */
