/* Apollo QuickList refresh at 0x4f5e84..0x4f5faf.
 * The four lower QuickList calls remain separate provider contracts. */
#include <stdint.h>

extern uint32_t audio_quicklist_refresh_lock_4ffac8(void);
extern uint32_t audio_quicklist_refresh_ready_4f5e18(void);
extern void audio_quicklist_refresh_unlock_4ffb26(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_log_wake_allowed(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_master_display_refresh(uint32_t, const void *, uint16_t,
                                              uint32_t); /* selected native 0x464bb2 */
extern void audio_quicklist_refresh_pending_4f5596(void);

static const char module[] = "quicklist.page";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\quicklist\\ui_quicklist_page.c";
static const char function[] = "quicklist_ui_data_update";
static const char lock_message[] = "Failed to lock storage";
static const char ready_message[] = "Failed to sync data from storage to UI";
static const char lock_compact[] = "[quicklist.page]Failed to lock storage";
static const char ready_compact[] = "[quicklist.page]Failed to sync data from storage to UI";

uint32_t audio_quicklist_refresh_4f5e84(void) {
    if (audio_quicklist_refresh_lock_4ffac8() == 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 1066u, lock_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, lock_compact, lock_compact);
        return UINT32_MAX;
    }
    if (audio_quicklist_refresh_ready_4f5e18() != 0u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(1u, module, path, function, 1072u, ready_message);
        if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x04000000u, ready_compact, ready_compact);
        audio_quicklist_refresh_unlock_4ffb26();
        return UINT32_MAX - 1u;
    }
    audio_quicklist_refresh_unlock_4ffb26();
    if (audio_log_wake_allowed() == 1u &&
        audio_quicklist_refresh_enabled_4434d0(1u) == 1u) {
        if (audio_uart_device_role_get() == 1u) {
            uint8_t packet[8];
            const volatile uint8_t *initial = (const volatile uint8_t *)(uintptr_t)0x0078eda4u;
            volatile uint8_t *selection = (volatile uint8_t *)(uintptr_t)0x20075041u;
            volatile uint32_t *index = (volatile uint32_t *)(uintptr_t)0x20074e28u;
            for (uint32_t i = 0; i < 8u; ++i) packet[i] = initial[i];
            packet[2] = *selection;
            packet[3] = (uint8_t)*index;
            packet[4] = (uint8_t)(*index >> 8);
            audio_uart_master_display_refresh(1u, packet, 6u, 0u);
        }
    } else {
            volatile uint8_t *state = (volatile uint8_t *)(uintptr_t)0x2012d57au;
            volatile uint16_t *index = (volatile uint16_t *)(uintptr_t)0x2012d574u;
            *state = *(volatile uint8_t *)(uintptr_t)0x20075041u;
            *index = (uint16_t)*(volatile uint32_t *)(uintptr_t)0x20074e28u;
            audio_quicklist_refresh_pending_4f5596();
            *state = 0u;
            *index = 0u;
    }
    return 0u;
}
