/* evenhub_loading_page_common_data_handler, native 0x492f8c..0x492fdb (literal
 * pool words in the evenhub_loading_Page.c pool 0x493510..0x49355f).
 * Stock source D:\01_workspace\s200_ap510b_iar_git\app\gui\EvenHub\evenhub_loading_Page.c;
 * the rest of that TU is ui/a-13-evenhub/evenhub_loading_page.c. UI registry row 06
 * (app id 0xffe) primary handler. Reconstructed 2026-10-21 (C3) from the 2.2.6.10
 * disassembly; compiles, byte identity not established.
 *
 * Registry primary handler ABI: (event type, data, length). The handler only logs the
 * event type. Stock ends with a dead "cmp r4, #0" and leaves r0 as the last log call's
 * result; 0 is returned here. */
#include <stdint.h>

extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *,
                               ...);                                            /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char tag[] = "evenhub.loading_page"; /* ROM 0x777594 */
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenHub\\evenhub_loading_Page.c"; /* ROM 0x6f3564 */
static const char data_fn[] = "evenhub_loading_page_common_data_handler";     /* ROM 0x73ecbc */
static const char data_type[] = "evenhub_loading_page_common_data_handler eventType = %d"; /* ROM 0x71edb8 */
static const char data_type_s[] =
    "[evenhub.loading_page]evenhub_loading_page_common_data_handler eventType = %d"; /* ROM 0x6ed1a8 */

uint32_t audio_uart_registry_callback_492f8c(uint32_t event, const uint8_t *data, uint32_t length);

/* Stock 0x00492F8C (evenhub_loading_page_common_data_handler) */
uint32_t audio_uart_registry_callback_492f8c(uint32_t event, const uint8_t *data, uint32_t length)
{
    (void)data;
    (void)length;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, tag, file, data_fn, 0x8cu, data_type, event);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, data_type_s, data_type_s, event);
    return 0u;
}
