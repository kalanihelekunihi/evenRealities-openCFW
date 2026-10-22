/* UI page registry contexts of the app-owned registry rows
 * (system/ui-registry/ui_registry_table.c, flash table 0x6a44b0). Same
 * 28-byte initialised .data layout as the system-owned rows in
 * system/S2-system-rtos-runtime-data/registry_context_data.c: +0 page id,
 * +4 page root object (set at runtime), +0x08..+0x13 page words,
 * +0x14..+0x17 page bytes, +0x18 page event handler. Values are from the
 * decoded startup init image (scatter record 0x75d3f4, RAM
 * 0x20000000..0x20004557); the size is the 0x1c stride to the next stock
 * object. Handlers are resolved by address (Thumb bit dropped). */
#include <stdint.h>

typedef struct {
    uint32_t page_id;      /* +0x00 */
    void *root;            /* +0x04 page root object */
    uint32_t word_08;      /* +0x08 */
    uint32_t word_0c;      /* +0x0c */
    uint32_t word_10;      /* +0x10 */
    uint8_t byte_14;       /* +0x14 */
    uint8_t byte_15;       /* +0x15 */
    uint8_t byte_16;       /* +0x16 */
    uint8_t byte_17;       /* +0x17 */
    void (*handler)(void); /* +0x18 page event handler */
} g2_app_page_context_t;
_Static_assert(sizeof(g2_app_page_context_t) == 0x1cu, "registry page context");

void aging_test_page_event_handler_43c450(void);       /* 0x43c450 */
void dashboard_page_event_handler_49e144(void);        /* 0x49e144 */
void even_ai_input_event_handler_4e2a5c(void);         /* 0x4e2a5c */
void message_notify_input_event_handler_4e1c42(void);  /* 0x4e1c42 */
void setting_page_event_handler_467d68(void);          /* 0x467d68 */
void silent_mode_refresh_callback(void);               /* 0x469470 */
void system_alert_page_event_handler_4d2c42(void);     /* 0x4d2c42 */
void system_close_page_event_handler(void);            /* 0x469fa2 */
void teleprompt_page_event_handler_589eb6(void);       /* 0x589eb6 */
void terminal_ui_input_filter(void);                   /* 0x5e444c */

/* RAM 0x20000044, row 00 page 0x104 (aging test). */
g2_app_page_context_t audio_uart_registry_context_20000044 = {
    0x104u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0xffu, 0x01u, aging_test_page_event_handler_43c450};
/* RAM 0x200005bc, row 03 page 0x1 (dashboard). */
g2_app_page_context_t audio_uart_registry_context_200005bc = {
    0x1u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x64u, 0x01u, dashboard_page_event_handler_49e144};
/* RAM 0x200009a4, row 05 page 0x7 (Even AI). */
g2_app_page_context_t audio_uart_registry_context_200009a4 = {
    0x7u, 0, 0x01000101u, 0xfau, 0xfau, 0x64u, 0x00u, 0xffu, 0x01u, even_ai_input_event_handler_4e2a5c};
/* RAM 0x20002cc4, row 13 page 0x4 (message notification). */
g2_app_page_context_t audio_uart_registry_context_20002cc4 = {
    0x4u, 0, 0x01000202u, 0xfau, 0xfau, 0x64u, 0x00u, 0x64u, 0x01u, message_notify_input_event_handler_4e1c42};
/* RAM 0x20003a40, row 25 page 0x9 (settings). */
g2_app_page_context_t audio_uart_registry_context_20003a40 = {
    0x9u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x00u, 0x01u, setting_page_event_handler_467d68};
/* RAM 0x20003a5c, row 26 page 0x10a (silent mode). */
g2_app_page_context_t audio_uart_registry_context_20003a5c = {
    0x10au, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0xffu, 0x01u, silent_mode_refresh_callback};
/* RAM 0x20003bd0, row 29 page 0x21 (system alert). */
g2_app_page_context_t audio_uart_registry_context_20003bd0 = {
    0x21u, 0, 0x01000002u, 0xfau, 0x0u, 0x64u, 0x00u, 0x96u, 0x01u, system_alert_page_event_handler_4d2c42};
/* RAM 0x20003bf0, row 30 page 0x22 (system close). */
g2_app_page_context_t audio_uart_registry_context_20003bf0 = {
    0x22u, 0, 0x01010202u, 0xfau, 0xfau, 0x4du, 0x00u, 0xa0u, 0x01u, system_close_page_event_handler};
/* RAM 0x20003da4, row 31 page 0x6 (teleprompt). */
g2_app_page_context_t audio_uart_registry_context_20003da4 = {
    0x6u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x00u, 0x01u, teleprompt_page_event_handler_589eb6};
/* RAM 0x20003e50, row 32 page 0x30 (terminal). */
g2_app_page_context_t audio_uart_registry_context_20003e50 = {
    0x30u, 0, 0x00000000u, 0x0u, 0x0u, 0x00u, 0x00u, 0x00u, 0x01u, terminal_ui_input_filter};
