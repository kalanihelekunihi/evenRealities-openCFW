/* MSG_COUNT callback list, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_msg_notif.c.
 * Native 0x4e1a48..0x4e1af7; literal pool 0x4e1b08..0x4e1b27.
 *
 * 12-byte callback manager at RAM 0x20073f84 named "MSG_COUNT" (ROM 0x78a58c).
 * The ANCC service initialises it (0x497398); the dashboard registers its
 * unread-count callback. CB_ANCC_NotifyMsgCount 0x4e1af8 is already defined
 * as audio_even_ai_ancc_display_clear_4e1af8 in drivers/display/even-ai. */
#include <stddef.h>
#include <stdint.h>

typedef void (*g2_msg_count_cb_t)(uint32_t event, const void *data);

extern uint8_t g2_audio_ancc_display_context_20073f84[]; /* RAM 0x20073f84, callback manager */

extern uint32_t audio_callback_mgr_init(void *manager, const char *name);   /* CALLBACK_MGR_Init 0x510108 */
extern uint32_t CALLBACK_MGR_Deinit(void *manager);                         /* 0x5101ae */
extern uint32_t audio_callback_mgr_register(void *manager, void *callback); /* CALLBACK_MGR_Register 0x510240 */
extern void audio_callback_mgr_unregister(void *manager, void *callback);  /* CALLBACK_MGR_Unregister 0x5103c4 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t,
                               const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char list_name[] = "MSG_COUNT";    /* ROM 0x78a58c */
static const char module_tag[] = "cb.msg_notif"; /* ROM 0x7856e0 */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\callback_mgr\\cb_msg_notif.c"; /* ROM 0x6e66c4 */
static const char register_fn[] = "CB_ANCC_RegisterMsgCountCallback";     /* ROM 0x752760 */
static const char unregister_fn[] = "CB_ANCC_UnregisterMsgCountCallback"; /* ROM 0x752784 */
static const char invalid_cb[] = "Invalid callback function";             /* ROM 0x76a000 */
static const char invalid_cb_short[] = "[cb.msg_notif]Invalid callback function"; /* ROM 0x748034 */

/* Expanded in place at each call site, as in stock. */
#define LOG_INVALID_CALLBACK(fn, line)                                                     \
    do {                                                                                   \
        if (audio_log_flags() & 2u)                                                        \
            audio_log_extended(1u, module_tag, source_file, (fn), (line), invalid_cb);     \
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))                          \
            (void)compress_log_output(0x04000000u, invalid_cb_short, invalid_cb_short);    \
    } while (0)

void CB_ANCC_InitMsgCountCallbacks(void) {
    (void)audio_callback_mgr_init(g2_audio_ancc_display_context_20073f84, list_name);
}

void CB_ANCC_DeinitMsgCountCallbacks(void) {
    (void)CALLBACK_MGR_Deinit(g2_audio_ancc_display_context_20073f84);
}

uint32_t CB_ANCC_RegisterMsgCountCallback(g2_msg_count_cb_t callback) {
    if (callback == NULL) {
        LOG_INVALID_CALLBACK(register_fn, 0x2au);
        return 0u;
    }
    return audio_callback_mgr_register(g2_audio_ancc_display_context_20073f84, (void *)callback);
}

void CB_ANCC_UnregisterMsgCountCallback(g2_msg_count_cb_t callback) {
    if (callback == NULL) {
        LOG_INVALID_CALLBACK(unregister_fn, 0x35u);
        return;
    }
    audio_callback_mgr_unregister(g2_audio_ancc_display_context_20073f84, (void *)callback);
}
