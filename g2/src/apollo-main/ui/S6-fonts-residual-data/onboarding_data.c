/* Onboarding main page storage (S6-fonts-residual storage-definition pass,
 * G2 2.2.6.10). Stock owner:
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\ui_onboarding_main_page.c.
 *
 * .data value from the decoded 0x20000000 init stream (scatter record
 * 0x75d3f4). Absolute placement is a linker obligation; compiling this file
 * does not establish byte identity. */
#include <stdint.h>

/* RAM 0x200042b0 (.data, = 5): number of feature cards in the onboarding
 * side menu. Its only stock user is ui_onboarding_menu_create_4ab6e4
 * (0x4ab6e4..0x4aba49, ui/x-05-onboarding/ui_onboarding_main_menu.c; literal
 * 0x4abc70): 0x4ab830 / 0x4ab83e load it to allocate two count * 4 object
 * arrays (heap_alloc_or_abort_51008a), 0x4ab916 uses it as the loop bound
 * over the 12-byte card table g2_onboarding_feature_cards_71aaac (ROM
 * 0x71aaac, ui/x-05-onboarding/onboarding_menu_data.c). */
int32_t g2_onboarding_feature_card_count_200042b0 = 5;
