/* Reconstructed semantic_pdt_distortion_screen_event at 0x005cf330.
 * The page calls are separate providers; the ROM assets and RAM placement
 * named below still need source ownership before a whole-image link. */
#include <stdint.h>
#include "distortion_screen_assets.h"

extern uint32_t audio_uart_page_43de82(uint32_t);
extern void audio_uart_page_43dfa4(uint32_t, uint32_t);
extern void audio_uart_page_43f09a(uint32_t, int32_t, int32_t);
extern void audio_uart_page_43f4c0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_43f506(uint32_t, uint32_t);
extern void audio_uart_page_43f568(uint32_t, uint32_t);
extern void audio_uart_page_43ded4(uint32_t, uint32_t);
extern void audio_uart_page_43f6b8(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_44104c(uint32_t);
extern void audio_uart_page_44120e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44121c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44122a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441238(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441246(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441254(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44127e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44129e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4412ec(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44130c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44131c(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44133a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441378(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441386(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_441394(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4413a2(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_4413b0(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44140e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44142e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44143e(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44145a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_44146a(uint32_t, uint32_t, uint32_t);
extern void audio_uart_page_48ba78(uint32_t, uint32_t);
extern void audio_uart_page_48ba92(uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t audio_uart_page_498668(uint32_t);
extern void audio_uart_page_498680(uint32_t, const void *);
extern uint32_t audio_uart_page_499416(uint32_t);
extern void audio_uart_page_49942e(uint32_t, uint32_t);
extern uint32_t audio_uart_page_460084(const void *);
extern uint32_t audio_uart_page_45fffe(const void *, uint32_t);
/* The stock literal points at the ring-list primary head cell. */
extern uint32_t audio_uart_ring_primary_head_cell;
extern uint32_t audio_uart_registry_context_20003064[];

/* Stock calls the out-of-line pad_all copy at 0x5cf2b4 with (object, 0, 0);
 * it is defined once, in ui/p-16-pdt-screens/pdt_screen_helpers.c. */
extern void semantic_zero_four_object_styles(uint32_t object, uint32_t value, uint32_t selector);

/* Stock 0x5cf32c..0x5cf32f (movs r0,#1; bx lr): input handler stored at
 * +0x18 of the page's UI-registry context (RAM 0x20003064, word 0x5cf32d). */
uint32_t semantic_distortion_predicate_true_5cf32c(uint32_t arg0, uint32_t arg1,
                                                   uint32_t code, const uint8_t *event) {
    (void)arg0;
    (void)arg1;
    (void)code;
    (void)event;
    return 1u;
}

uint32_t audio_uart_registry_callback_5cf330(uint32_t event, uint32_t arg2,
                                              uint32_t value, uint32_t parent) {
    (void)arg2;
    (void)value;
    if (event != 2u) return 0;
    uint32_t root = audio_uart_page_43de82(parent);
    audio_uart_distortion_root_2007487c = root;
    audio_uart_page_43dfa4(root, 0x10);
    audio_uart_page_43f506(root, 0x280);
    audio_uart_page_43f568(root, 0x1e0);
    audio_uart_page_44127e(root, audio_uart_page_44104c(0), 0);
    audio_uart_page_44129e(root, 0xff, 0);
    audio_uart_page_44131c(root, 0, 0);
    semantic_zero_four_object_styles(root, 0, 0);

    uint32_t top = audio_uart_page_43de82(root);
    audio_uart_page_43dfa4(top, 0x10);
    audio_uart_page_43f09a(top, 0, 0x32);
    audio_uart_page_43f506(top, 0x23e);
    audio_uart_page_43f568(top, 0xce);
    audio_uart_page_44127e(top, audio_uart_page_44104c(0), 0);
    audio_uart_page_44129e(top, 0, 0);
    audio_uart_page_44131c(top, 2, 0);
    audio_uart_page_4412ec(top, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_44130c(top, 0xff, 0);
    audio_uart_page_44133a(top, 0, 0);
    audio_uart_page_441378(top, 0, 0);
    audio_uart_page_441386(top, 0, 0);
    audio_uart_page_4413b0(top, 0, 0);
    audio_uart_page_441394(top, 0, 0);
    audio_uart_page_4413a2(top, 0, 0);
    semantic_zero_four_object_styles(top, 0, 0);
    audio_uart_page_44120e(top, 0, 0);
    audio_uart_page_44121c(top, 0, 0);
    audio_uart_page_44122a(top, 0, 0);
    audio_uart_page_441238(top, 0, 0);
    audio_uart_page_44146a(top, 0, 0);
    audio_uart_page_44140e(top, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_44142e(top, 0xff, 0);

    uint32_t center = audio_uart_page_43de82(top);
    audio_uart_page_43f4c0(center, 0x3fffffff, 0x3fffffff);
    audio_uart_page_44129e(center, 0, 0);
    audio_uart_page_44131c(center, 0, 0);
    semantic_zero_four_object_styles(center, 0, 0);
    audio_uart_page_48ba78(center, 1);
    audio_uart_page_48ba92(center, 2, 2, 2);
    audio_uart_page_441246(center, 8, 0);
    audio_uart_page_43f6b8(center, 9, 0, 0);

    uint32_t child = audio_uart_page_43de82(center);
    audio_uart_page_43f4c0(child, 0x3fffffff, 0x3fffffff);
    audio_uart_page_44129e(child, 0, 0);
    audio_uart_page_44131c(child, 0, 0);
    semantic_zero_four_object_styles(child, 0, 0);
    audio_uart_page_48ba78(child, 0);
    audio_uart_page_48ba92(child, 2, 2, 2);
    audio_uart_page_441254(child, 8, 0);
    uint32_t icon = audio_uart_page_498668(child);
    audio_uart_page_498680(icon, &audio_uart_distortion_asset_769f58);
    audio_uart_page_43f506(icon, 0x18);
    audio_uart_page_43f568(icon, 0x18);
    audio_uart_page_43ded4(icon, 0x10000);
    audio_uart_page_43dfa4(icon, 0x10);

    uint32_t label = audio_uart_page_499416(child);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(
        audio_uart_distortion_text_736af4,
        audio_uart_page_460084(audio_uart_distortion_text_736af4)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0);
    label = audio_uart_page_499416(center);
    audio_uart_page_44140e(label, audio_uart_page_44104c(0xffffff), 0);
    audio_uart_page_49942e(label, audio_uart_page_45fffe(
        audio_uart_distortion_text_736b24,
        audio_uart_page_460084(audio_uart_distortion_text_736b24)));
    audio_uart_page_44143e(label, audio_uart_ring_primary_head_cell, 0);
    audio_uart_page_44145a(label, 2, 0);
    audio_uart_registry_context_20003064[1] = root;
    return 0;
}
