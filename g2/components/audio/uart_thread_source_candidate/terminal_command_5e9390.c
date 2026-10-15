/* Native terminal_action_agent_content 0x5e9390. */
#include <stdint.h>

extern uint32_t audio_terminal_message_session_matches(uint32_t, const char *);
extern uint8_t audio_terminal_data_append_agent_content(const void *, uint16_t *);
extern uint32_t audio_terminal_agent_text_token(uint8_t, uint16_t);
extern uint32_t audio_terminal_agent_trigger_token(uint32_t, uint32_t);
extern uint32_t audio_terminal_request_display(uint8_t, uint32_t);
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint8_t audio_terminal_ui_mode; /* native RAM base+0x275 */
struct audio_terminal_output_tracking {
    uint8_t active;
    uint8_t reserved[3];
    uint32_t count;
};
extern struct audio_terminal_output_tracking audio_terminal_output_tracking;
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);

static const char session_name[] = "agent content"; /* native ROM 0x7898d0 */
static const char module[]="terminal.pb";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_pb_msg_handler.c";
static const char function[]="terminal_action_agent_content";
static const char ignored[]="ignore terminal agent text content: op=%d, id=%u, text_len=%u";
static const char ignored_short[]="[terminal.pb]ignore terminal agent text content: op=%d, id=%u, text_len=%u";
static const char skip[]="skip terminal agent text append: op=%d id=%u style=%d event=%d";
static const char skip_short[]="[terminal.pb]skip terminal agent text append: op=%d id=%u style=%d event=%d";
static const char replay[]="replay output_start while waiting output_end: id=%lu";
static const char replay_short[]="[terminal.pb]replay output_start while waiting output_end: id=%lu";
static const char drop_start[]="drop tool_start within 2s: id=%lu elapsed=%lu";
static const char drop_start_short[]="[terminal.pb]drop tool_start within 2s: id=%lu elapsed=%lu";
static const char nonprocessing[]="drop content trigger event in non-processing state=%d event=%d style=%d";
static const char nonprocessing_short[]="[terminal.pb]drop content trigger event in non-processing state=%d event=%d style=%d";
static const char summary[]="recv terminal agent content: op=%d id=%u refresh=%u idx=%u style=%d event=%d in_proc=%d wait=%d->%d out_raw=%d trigger=0x%lx seed=%lu text_len=%u req_text=%d req_event=%d";
static const char summary_short[]="[terminal.pb]recv terminal agent content: op=%d id=%u refresh=%u idx=%u style=%d event=%d in_proc=%d wait=%d->%d out_raw=%d trigger=0x%lx seed=%lu text_len=%u req_text=%d req_event=%d";
static const char text_line[]="len: %d, text: %s";
static const char text_line_short[]="[terminal.pb]len: %d, text: %s";

static uint16_t load16(const uint8_t *p) {
    return (uint16_t)p[0] | (uint16_t)((uint16_t)p[1] << 8);
}
static uint32_t load32(const uint8_t *p) {
    return (uint32_t)p[0] | (uint32_t)p[1] << 8 |
           (uint32_t)p[2] << 16 | (uint32_t)p[3] << 24;
}

uint32_t audio_terminal_command_5e9390(const void *payload, uint32_t length) {
    (void)length;
    if (payload == 0) return UINT32_MAX;
    const uint8_t *const packet = (const uint8_t *)payload;
    if (audio_terminal_message_session_matches(load32(packet + 0x210u),
                                               session_name) == 0u) return 0u;

    const uint16_t text_length = load16(packet + 2u);
    const uint32_t session = load32(packet + 0x208u);
    const uint8_t opcode = packet[0];
    const uint8_t event = packet[0x20cu];
    uint8_t text_sent = 0u;
    uint8_t trigger_sent = 0u;
    uint16_t appended_length = 0xffffu;
    uint8_t append_result = 0u;

    if (text_length != 0u) {
        append_result = audio_terminal_data_append_agent_content(packet,
                                                                 &appended_length);
        if (append_result != 0u) {
            uint32_t token = audio_terminal_agent_text_token(append_result,
                                                              appended_length);
            (void)audio_terminal_request_display(0x12u, token);
            text_sent = 1u;
        } else {
            if (audio_log_flags() & 2u)
                audio_log_extended(2u,module,path,function,0x215u,ignored,
                                   packet[0x204u],session,text_length);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x8c00000u,ignored_short,ignored_short,
                                            packet[0x204u],session,text_length);
        }
    } else {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u,module,path,function,0x21du,skip,
                               packet[0x204u],session,opcode,event);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x11000000u,skip_short,skip_short,
                                        packet[0x204u],session,opcode,event);
    }

    const uint8_t trigger = event == 3u ||
                            (text_length != 0u && opcode == 0u && event != 4u);
    const uint8_t in_processing=audio_terminal_ui_mode==7u;
    const uint8_t was_waiting=audio_terminal_output_tracking.active!=0u;
    uint32_t flags = 0u;
    uint32_t token_tick = 0u;
    if (in_processing) {
        uint8_t has_tool_end_tick = 0u;
        if (event == 4u) audio_terminal_output_tracking.active = 0u;
        if (event == 2u) flags |= 2u;
        if (event == 4u) {
            token_tick = g2_flashdb_candidate_tick();
            flags |= 9u;
            audio_terminal_output_tracking.count = token_tick;
            has_tool_end_tick = 1u;
        }
        if (trigger) {
            flags |= 4u;
            if (audio_terminal_output_tracking.active == 0u)
                audio_terminal_output_tracking.active = 1u;
            else {
                if (audio_log_flags() & 2u)
                    audio_log_extended(4u,module,path,function,0x23du,replay,session);
                if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                    (void)compressed_log_output(0x10400000u,replay_short,replay_short,session);
            }
        }
        if (event == 1u) {
            uint32_t now = g2_flashdb_candidate_tick();
            uint32_t previous = audio_terminal_output_tracking.count;
            if (previous == 0u || now - previous > 1999u) {
                audio_terminal_output_tracking.count = now;
                flags |= 1u;
            } else {
                uint32_t elapsed=now-previous;
                if (audio_log_flags() & 2u)
                    audio_log_extended(4u,module,path,function,0x24au,drop_start,
                                       session,elapsed);
                if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                    (void)compressed_log_output(0x10800000u,drop_start_short,
                                                drop_start_short,session,elapsed);
            }
        }
        if (flags != 0u) {
            if (!has_tool_end_tick)
                token_tick = session != 0u ? session : g2_flashdb_candidate_tick();
            uint32_t token = audio_terminal_agent_trigger_token(flags, token_tick);
            (void)audio_terminal_request_display(0x13u, token);
            trigger_sent = 1u;
        }
    } else if (event != 0u || trigger) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u,module,path,function,599u,nonprocessing,
                               audio_terminal_ui_mode,event,opcode);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10c00000u,nonprocessing_short,
                                        nonprocessing_short,audio_terminal_ui_mode,
                                        event,opcode);
    }
    uint8_t waiting_after=audio_terminal_output_tracking.active!=0u;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u,module,path,function,0x25eu,summary,
                           packet[0x204u],session,append_result,appended_length,opcode,event,
                           in_processing,was_waiting,waiting_after,trigger,flags,token_tick,
                           text_length,text_sent,trigger_sent);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output((flags<<22)|0xc000000u,summary_short,summary_short,
                                    packet[0x204u],session,append_result,appended_length,
                                    opcode,event,in_processing,was_waiting,waiting_after,
                                    trigger,flags,token_tick,text_length,text_sent,trigger_sent);
    if (audio_log_flags() & 2u)
        audio_log_extended(3u,module,path,function,0x25fu,text_line,
                           text_length,packet+4u);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0xc800000u,text_line_short,text_line_short,
                                    text_length,packet+4u);
    if (text_sent == 0u && trigger_sent == 0u && text_length != 0u)
        return UINT32_MAX;
    return 0u;
}
