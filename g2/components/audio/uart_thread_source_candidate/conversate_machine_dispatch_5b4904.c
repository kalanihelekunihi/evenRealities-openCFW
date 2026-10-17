/* Native conversate_machine_handler at 0x5b4904..0x5b4a8f. */
#include <stdint.h>

extern uint8_t audio_conversate_machine_context_200e3aec;
extern const char *audio_conversate_event_name_5b48f8(uint32_t);
extern uint32_t audio_conversate_action_5b4a90(void *, void *, void *);
extern uint32_t audio_conversate_action_5b4cc8(void *, void *, void *);
extern uint32_t audio_conversate_action_5b4d10(void *, void *, void *);
extern uint32_t audio_conversate_action_5b4e98(void *, void *, void *);
extern uint32_t audio_conversate_action_5b4dba(void *, void *, void *);
extern uint32_t audio_conversate_action_5b5150(void *, void *, void *);
extern uint32_t audio_conversate_action_5b52e0(void *, void *, void *);
extern uint32_t audio_conversate_action_5b4f72(void *, void *, void *);
extern uint32_t audio_conversate_action_5b5428(void *, void *, void *);
extern uint32_t audio_conversate_action_5b55b4(void *, void *, void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern void audio_log_simple(uint32_t, const char *, const char *, ...);

typedef uint32_t (*action_t)(void *, void *, void *);
static const action_t actions[13] = {
    0, audio_conversate_action_5b4a90, audio_conversate_action_5b4cc8,
    audio_conversate_action_5b4d10, audio_conversate_action_5b4e98,
    audio_conversate_action_5b4dba, 0, 0, audio_conversate_action_5b5150,
    audio_conversate_action_5b52e0, audio_conversate_action_5b4f72,
    audio_conversate_action_5b5428, audio_conversate_action_5b55b4,
};

static const char module[] = "conversate";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\conversate\\conversate_pb_msg_handler.c";
static const char function[] = "conversate_machine_handler";
static const char invalid[] = "event is invalid";
static const char invalid_short[] = "[conversate]event is invalid";
static const char received[] = "recv event [%d|%s]";
static const char received_short[] = "[conversate]recv event [%d|%s]";
static const char no_action[] = "event[%d|%s] no match action";
static const char no_action_short[] = "[conversate]event[%d|%s] no match action";
static const char action_failed[] = "action execution failed";
static const char action_failed_short[] = "[conversate]action execution failed";

uint32_t audio_conversate_dispatch_5b4904(uint8_t event, void *arg1,
                                           void *arg2, void *unused) {
    (void)unused;
    if (event >= 13u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, function, 89u, invalid);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x04000000u, invalid_short, invalid_short);
        return UINT32_MAX;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module, path, function, 93u, received,
                           event, audio_conversate_event_name_5b48f8(event));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x0c800000u, received_short, received_short,
                         event, audio_conversate_event_name_5b48f8(event));
    action_t action = actions[event];
    if (!action) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 100u, no_action,
                               event, audio_conversate_event_name_5b48f8(event));
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08800000u, no_action_short, no_action_short,
                             event, audio_conversate_event_name_5b48f8(event));
        return UINT32_MAX;
    }
    uint32_t status = action(&audio_conversate_machine_context_200e3aec, arg1, arg2);
    if (status != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(2u, module, path, function, 107u, action_failed);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            audio_log_simple(0x08000000u, action_failed_short, action_failed_short);
    }
    return status;
}
