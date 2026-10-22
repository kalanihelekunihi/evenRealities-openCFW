/* Onboarding side-menu storage. Stock owner
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c
 * (users ui_onboarding_menu_create_4ab6e4 / ui_onboarding_main_destroy_4abba4
 * in ui_onboarding_main_menu.c). ROM bytes from ota_s200_firmware_ota.bin
 * (VA = file offset + 0x437fe0); .data values from the decoded 0x20000000
 * init stream (scatter record 0x75d3f4); other cells are .bss. Absolute
 * placement is a linker obligation; compiling this file does not establish
 * byte identity. The card count cell 0x200042b0 is defined in
 * ui/S6-fonts-residual-data/onboarding_data.c. */
#include <stdint.h>

typedef struct {
    const void *icon;      /* +0x00 lv_image_dsc_t */
    const char *text_key;  /* +0x04 i18n key */
    int32_t card_id;       /* +0x08 */
} g2_onboarding_feature_card_t;
_Static_assert(sizeof(g2_onboarding_feature_card_t) == 12u, "stock card stride");

extern const struct g2_icon_descriptor g2_img_dsc_76a24c; /* ROM 0x76a24c conversate icon */
extern const struct g2_icon_descriptor g2_img_dsc_772960; /* ROM 0x772960 teleprompt icon */
extern const struct g2_icon_descriptor g2_img_dsc_773a00; /* ROM 0x773a00 translate icon */
extern const struct g2_icon_descriptor g2_img_dsc_76e638; /* ROM 0x76e638 navigate icon */
extern const struct g2_icon_descriptor g2_img_dsc_76b6f8; /* ROM 0x76b6f8 Even AI icon */

static const char card_key_784914[] = "ID_MENU_CONVERSATE"; /* ROM 0x784914 */
static const char card_key_784928[] = "ID_MENU_TELEPROMPT"; /* ROM 0x784928 */
static const char card_key_78493c[] = "ID_MENU_TRANSLATE";  /* ROM 0x78493c */
static const char card_key_784950[] = "ID_MENU_NAVIGATE";   /* ROM 0x784950 */
static const char card_key_789dd0[] = "ID_MENU_EVEN_AI";    /* ROM 0x789dd0 */

/* ROM 0x71aaac..0x71aae7: five feature cards (the "[onboarding.news..."
 * string follows at 0x71aae8). Only literal user: 0x4abc78. */
const g2_onboarding_feature_card_t g2_onboarding_feature_cards_71aaac[5] = {
    {&g2_img_dsc_76a24c, card_key_784914, 1},
    {&g2_img_dsc_772960, card_key_784928, 2},
    {&g2_img_dsc_773a00, card_key_78493c, 3},
    {&g2_img_dsc_76e638, card_key_784950, 4},
    {&g2_img_dsc_76b6f8, card_key_789dd0, 5},
};

/* Cells whose only literal-pool reference is the destroy path
 * (0x4abc94 / 0x4abca0 / 0x4abca4 / 0x4abca8); purpose not recovered. */
int32_t g2_onboarding_state_20074d74;       /* RAM 0x20074d74 */
int32_t g2_onboarding_state_20074d80;       /* RAM 0x20074d80 */
int32_t g2_onboarding_state_20074d84;       /* RAM 0x20074d84 */
int32_t g2_onboarding_state_20004290 = 200; /* RAM 0x20004290 (.data, init record 0x75d3f4: 0xc8) */

/* Touch-tip view objects (ui_onboarding_main_touch_tips_create_4aae38;
 * literals 0x4abbf4 / 0x4abbfc are their only references). 0x20074cfc and
 * 0x20074d08 are in ui/S4-ui-a-data/onboarding_data.c. */
void *g2_onboarding_tip_frame_20074d00;      /* RAM 0x20074d00 */
void *g2_onboarding_tip_anim_image_20074d04; /* RAM 0x20074d04 */
