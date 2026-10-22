/* Native AppUiDisplayPasskey 0x4bd7fa and AppUiDisplayConfirmValue 0x4bd91e.
 * Their ARM entry frames carry the inherited fourth log argument and return
 * the outgoing IAR varargs words after a gated extended log. */
#include <stdint.h>

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *, const char *, uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern void audio_ble_wsf_trace(const char *, const char *, ...);
extern uintptr_t audio_ble_ui_callback_cells[]; /* live 0x20073f60, callback +4 */

static const char info[] = "INFO";
static const char err[] = "ERR";
static const char warn[] = "WARN";
static const char app[] = "APP";
static const char hci[] = "HCI";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_ui.c";
static const char passkey_message[] __attribute__((used)) = ">>> Passkey: %d <<<";
static const char confirm_message[] __attribute__((used)) = ">>> Confirm Value: %d <<<";
static const char passkey_function[] __attribute__((used)) = "AppUiDisplayPasskey";
static const char confirm_function[] __attribute__((used)) = "AppUiDisplayConfirmValue";

void audio_ble_pair_ui_diagnostic_body(uint32_t *saved, const char *message,
                                        const char *function, uint32_t line)
{
    const uint32_t value = saved[0];
    uint8_t level = 0u;
    if (audio_ble_hci_vendor_log_enabled_4c9c50() &&
        audio_l2c_strncmp(info, err, 3u) == 0) level = 1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() &&
             audio_l2c_strncmp(info, warn, 4u) == 0) level = 2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() &&
             audio_l2c_strncmp(info, info, 4u) == 0) level = 3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50()) level = 4u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
             audio_l2c_strncmp(app, hci, 3u) != 0)
        audio_ble_wsf_trace(info, message, value);

    if (level != 0u && (audio_log_level() & 2u)) {
        saved[0] = line;
        saved[1] = (uint32_t)(uintptr_t)message;
        saved[2] = value;
        if (level == 1u)
            audio_log_extended(level, app, path, function, line, message, value, saved[3]);
        else
            audio_log_extended(level, app, path, function, line, message, value);
    }
    const uintptr_t callback = audio_ble_ui_callback_cells[1];
    if (callback != 0u)
        ((void (*)(uint32_t, uint32_t))callback)(line == 0xb7u ? 15u : 16u, value);
}

/* Stock 0x004BD7FA (FUN_004bd7fa, AppUiDisplayPasskey) */
__attribute__((naked)) void audio_ble_pair_passkey_trace(uint32_t value __attribute__((unused)))
{
    __asm__ volatile(
        "push {r0, r1, r2, r3, r4, lr}\n"
        "mov r0, sp\n"
        "ldr r1, =passkey_message\n"
        "ldr r2, =passkey_function\n"
        "movs r3, #0xb7\n"
        "bl audio_ble_pair_ui_diagnostic_body\n"
        "pop {r0, r1, r2, r3, r4, pc}\n");
}

/* Stock 0x004BD91E (FUN_004bd91e, AppUiDisplayConfirmValue) */
__attribute__((naked)) void audio_ble_pair_compare_trace(uint32_t value __attribute__((unused)))
{
    __asm__ volatile(
        "push {r0, r1, r2, r3, r4, lr}\n"
        "mov r0, sp\n"
        "ldr r1, =confirm_message\n"
        "ldr r2, =confirm_function\n"
        "movs r3, #0xca\n"
        "bl audio_ble_pair_ui_diagnostic_body\n"
        "pop {r0, r1, r2, r3, r4, pc}\n");
}
