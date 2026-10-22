/* UI page registry contexts of the system-owned registry rows
 * (system/ui-registry/ui_registry_table.c, flash table 0x6a44b0). Each is a
 * 28-byte initialised .data page context: +0 page id, +4 page root object
 * (set at runtime), +0x08..+0x13 page words, +0x14..+0x17 page bytes, +0x18
 * page event handler. Values are from the decoded startup init image (RAM
 * 0x20000000..0x20004557); the size is the stride to the next stock object
 * (0x1c in every case). Handlers are resolved by address. */
#include <stdint.h>

typedef struct {
    uint32_t page_id;     /* +0x00 */
    void *root;           /* +0x04 page root object */
    uint32_t word_08;     /* +0x08 */
    uint32_t word_0c;     /* +0x0c (menu: animation time) */
    uint32_t word_10;     /* +0x10 */
    uint8_t byte_14;      /* +0x14 */
    uint8_t byte_15;      /* +0x15 */
    uint8_t byte_16;      /* +0x16 */
    uint8_t byte_17;      /* +0x17 */
    void (*handler)(void); /* +0x18 page event handler */
} g2_ui_page_context_t;
_Static_assert(sizeof(g2_ui_page_context_t) == 0x1cu, "registry page context");

void evenhub_loading_page_event_handler_492cee(void); /* 0x492cee */
void evenhub_page_event_handler_4e0d3a(void); /* 0x4e0d3a */
void menu_key_handler_463204(void); /* 0x463204 */
void navigation_page_event_handler_585ce0(void); /* 0x585ce0 */
void onboarding_page_event_handler(void); /* 0x468c68 */
void translate_page_event_handler_59efe0(void); /* 0x59efe0 */

/* RAM 0x20000b1c */
g2_ui_page_context_t audio_uart_registry_context_20000b1c = {
    0xffeu, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x64u, 0x01u, evenhub_loading_page_event_handler_492cee};
/* RAM 0x20000b38 */
g2_ui_page_context_t audio_uart_registry_context_20000b38 = {
    0xe0u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x64u, 0x01u, evenhub_page_event_handler_4e0d3a};
/* RAM 0x20002ca8 */
g2_ui_page_context_t audio_uart_registry_context_20002ca8 = {
    0x3u, 0, 0x01000000u, 0xfau, 0x0u, 0x64u, 0x00u, 0xffu, 0x01u, menu_key_handler_463204};
/* RAM 0x20002ce0 */
g2_ui_page_context_t audio_uart_registry_context_20002ce0 = {
    0x8u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x64u, 0x01u, navigation_page_event_handler_585ce0};
/* RAM 0x20002e34 */
g2_ui_page_context_t audio_uart_registry_context_20002e34 = {
    0x10u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x64u, 0x01u, onboarding_page_event_handler};
/* RAM 0x2000418c */
g2_ui_page_context_t audio_uart_registry_context_2000418c = {
    0x5u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x00u, 0x01u, translate_page_event_handler_59efe0};
