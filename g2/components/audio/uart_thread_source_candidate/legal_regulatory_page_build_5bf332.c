/* LegalRegulatory page builder, stock 0x5bf332..0x5bf7b7. The slot indices
 * name the authenticated 38-row resource table beginning at 0x5bf8ac. */
#include <stdint.h>
#include "legal_regulatory_assets.h"

#define ASSET(slot) (audio_legal_asset_slots[((slot) - 0x5bf8acu) / 4u])

extern uint32_t audio_legal_regulatory_root_200746a4;
extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f6b8(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f6d6(uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_441246(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44133a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441378(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4413be(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44e368(uint32_t, uint32_t);
extern void audio_uart_page_44e3ca(uint32_t, uint32_t);
extern void audio_uart_page_48ba78(uint32_t, uint32_t);
extern void audio_uart_page_48ba92(uint32_t, uint32_t, uint32_t, uint32_t);
extern void audio_legal_regulatory_zero_styles_5bf114(uint32_t, uint32_t, uint32_t);
extern uint32_t audio_legal_regulatory_panel_5bf24e(uint32_t);
extern uint32_t audio_legal_regulatory_label_5bf298(uint32_t, const void *);
extern uint64_t audio_legal_regulatory_icon_5bf2f8(uint32_t, const void *, uint32_t, uint32_t);

uint32_t audio_legal_regulatory_build_5bf332(uint32_t parent) {
    uint32_t root = audio_uart_page_43de82(parent);
    audio_legal_regulatory_root_200746a4 = root;
    audio_uart_page_43dfa4(root, 0x370u);
    audio_uart_page_43f4c0(root, 0x240u, 0x120u);
    audio_uart_page_43f09a(root, 0, 0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0u), 0u);
    audio_uart_page_44129e(root, 0xffu, 0u);
    audio_uart_page_44131c(root, 0u, 0u);
    audio_uart_page_44133a(root, 0u, 0u);
    audio_uart_page_441378(root, 0u, 0u);
    audio_uart_page_441386(root, 0u, 0u);
    audio_uart_page_4413be(root, 0u, 0u);
    audio_uart_page_44146a(root, 0u, 0u);
    audio_legal_regulatory_zero_styles_5bf114(root, 0u, 0u);
    audio_uart_page_48ba78(root, 1u);
    audio_uart_page_48ba92(root, 0u, 0u, 0u);
    audio_uart_page_441246(root, 0x1cu, 0u);
    audio_uart_page_43ded4(root, 0x10u);
    audio_uart_page_44e368(root, 1u);
    audio_uart_page_44e3ca(root, 0xcu);

    uint32_t panel = audio_legal_regulatory_panel_5bf24e(root);
    uint32_t item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8ac));
    audio_uart_page_43f6b8(item, 1u, 0u, 0u);
    panel = audio_legal_regulatory_panel_5bf24e(root);
    uint32_t previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8b0));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8b4));
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);
    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8b8));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8bc));
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);
    uint32_t anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(
        panel, ASSET(0x5bf8c0), 0u, 0u);
    audio_uart_page_43f6d6(anchor, item, 0xdu, 0u, 8u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8c4));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8c8));
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8cc));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8d0));
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf8d4), 0u, 0u);
    audio_uart_page_43f6d6(anchor, item, 0xdu, 0u, 8u);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8d8));
    audio_uart_page_43f6d6(previous, anchor, 0xdu, 0u, 0x1cu);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8dc));
    audio_uart_page_43f6d6(item, previous, 0xdu, 0u, 0x1cu);
    anchor = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8e0));
    audio_uart_page_43f6d6(anchor, item, 0xdu, 0u, 0x1cu);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8e4));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf8e8), 0u, 0u);
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8ec));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf8f0), 0u, 0u);
    audio_uart_page_43f6b8(anchor, 1u, 0xf0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8f4));
    audio_uart_page_43f6d6(item, anchor, 0xdu, 0u, 8u);
    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf8f8));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf8fc), 0u, 0u);
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf900));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf904), 0u, 0u);
    audio_uart_page_43f6b8(item, 1u, 0xf0u, 0u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf908));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf90c), 0u, 0u);
    audio_uart_page_43f6b8(anchor, 1u, 0xf0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf910));
    audio_uart_page_43f6d6(item, anchor, 0xdu, 0u, 8u);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf914));
    audio_uart_page_43f6d6(previous, item, 0xdu, 0u, 8u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf90c), 0u, 0u);
    audio_uart_page_43f6d6(anchor, previous, 0xdu, 0u, 0x1cu);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf918));
    audio_uart_page_43f6d6(item, anchor, 0xdu, 0u, 8u);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf91c));
    audio_uart_page_43f6d6(previous, item, 0xdu, 0u, 8u);

    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf920));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf924), 0u, 0u);
    audio_uart_page_43f6b8(anchor, 1u, 0xf0u, 0u);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf928));
    audio_uart_page_43f6d6(item, anchor, 0x14u, 8u, 0u);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf92c));
    audio_uart_page_43f6d6(previous, anchor, 0xdu, 0u, 8u);
    anchor = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf930), 0u, 0u);
    audio_uart_page_43f6d6(anchor, previous, 0xdu, 0u, 0x1cu);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf934));
    audio_uart_page_43f6d6(item, anchor, 0xdu, 0u, 8u);
    panel = audio_legal_regulatory_panel_5bf24e(root);
    item = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf938));
    audio_uart_page_43f6b8(item, 1u, 0u, 0u);
    panel = audio_legal_regulatory_panel_5bf24e(root);
    previous = audio_legal_regulatory_label_5bf298(panel, ASSET(0x5bf93c));
    audio_uart_page_43f6b8(previous, 1u, 0u, 0u);
    item = (uint32_t)audio_legal_regulatory_icon_5bf2f8(panel, ASSET(0x5bf940), 0u, 0u);
    audio_uart_page_43f6d6(item, previous, 0xdu, 0u, 0u);
    return 0u;
}
