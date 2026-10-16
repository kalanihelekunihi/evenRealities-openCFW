/* Native setting_data_recv_handler 0x466976..0x466abc. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *,
                               const char *, uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern uint32_t audio_setting_dispatch_message_466abc(const uint8_t *);
extern uint32_t audio_setting_serialize_response_49b900(void);
extern uint32_t audio_setting_serialize_local_response_49ba58(void);

static const char module[] = "setting";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c";
static const char function[] = "setting_data_recv_handler";
static const char null_message[] = "pMessage is NULL";
static const char null_short[] = "[setting]pMessage is NULL";
static const char app_failure[] = "setting respond to app serialize failed: %d";
static const char app_failure_short[] = "[setting]setting respond to app serialize failed: %d";
static const char processing[] = "Processing APP request";
static const char processing_short[] = "[setting]Processing APP request";
static const char local_failure[] = "setting respond with local data serialize failed: %d";
static const char local_failure_short[] = "[setting]setting respond with local data serialize failed: %d";

uint32_t audio_setting_process_data_466976(const uint8_t *message) {
    if (message == 0) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u,module,path,function,0x7du,null_message);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x08000000u,null_short,null_short);
        return 1u;
    }
    uint16_t kind=(uint16_t)message[8] | ((uint16_t)message[9] << 8);
    if (kind == 3u) {
        (void)audio_setting_dispatch_message_466abc(message);
        uint32_t error=audio_setting_serialize_response_49b900();
        if (error != 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(4u,module,path,function,0x88u,app_failure,error);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x10400000u,app_failure_short,
                                            app_failure_short,error);
        }
    } else if (kind == 4u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u,module,path,function,0x8bu,processing);
        if ((audio_log_flags() & 1u) != 0u ||
            (audio_log_flags() & 4u) != 0u)
            (void)compressed_log_output(0x10000000u,processing_short,processing_short);
        uint32_t error=audio_setting_serialize_local_response_49ba58();
        if (error != 0u) {
            if ((audio_log_flags() & 2u) != 0u)
                audio_log_extended(4u,module,path,function,0x90u,local_failure,error);
            if ((audio_log_flags() & 1u) != 0u ||
                (audio_log_flags() & 4u) != 0u)
                (void)compressed_log_output(0x10400000u,local_failure_short,
                                            local_failure_short,error);
        }
    }
    return 0u;
}
