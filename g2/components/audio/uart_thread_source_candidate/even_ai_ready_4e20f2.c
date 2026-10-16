/* Candidate for native EvenAI async update 0x4e20f2.
 * The state transitions are source-translated. Enabled logging, descendant
 * callees, dynamic text lengths, and callback behavior need native oracles.
 */
#include <stdint.h>

extern uint8_t audio_even_ai_service_state_2006ed10[0x218];
extern uint8_t audio_even_ai_ready_state_2006f138[0x218];
extern uint8_t audio_even_ai_config_state_20074974[3];
extern uint8_t audio_uart_display_state[2];
extern uint32_t audio_even_ai_text_stream_handle_20074c04;
extern uint8_t audio_even_ai_text_pending_200f39b4[0x400];
extern uint8_t audio_even_ai_text_merged_200f3db4[0x400];
extern void audio_even_ai_state_lock_4e1fa6(void);
extern void audio_even_ai_state_unlock_4e1fbe(void);
extern uint32_t audio_quicklist_refresh_enabled_4434d0(uint32_t);
extern uint8_t audio_ux_get_system_ble_status(void);
extern uint32_t audio_even_ai_app_acquire_54f380(uint32_t);
extern void audio_even_ai_timer_start_all_4e31a0(uint32_t);
extern void audio_even_ai_init_text_stream_4e551e(void);
extern void audio_even_ai_stop_current_streaming_4e557c(uint32_t);
extern void audio_even_ai_common_timer_stop_4e2e86(void);
extern void audio_even_ai_display_ctrl_4e1fd2(uint32_t, const void *, uint32_t);
extern const char *audio_text_stream_pending_text_552ce8(uint32_t);
extern uint32_t audio_text_stream_set_text_552c20(uint32_t, const char *, uint32_t,
                                                   uint32_t, uint32_t);
extern uint32_t audio_text_stream_copy_bytes_553274(uint32_t, uint32_t, uint32_t);
extern uint8_t audio_even_ai_stream_interval_get_4e550a(void);
extern void audio_even_ai_ancc_state_sync_497cf0(uint32_t, uint32_t);
extern void audio_even_ai_sync_remote_4973f4(uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char log_module[] = "even_ai.page";
static const char log_path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai.c";
static const char log_function[] = "even_ai_async_update_data";
static const char action_text[] = "[even ai]action_id = %d, action_type = %d";
static const char action_short[] = "[even_ai.page][even ai]action_id = %d, action_type = %d";
static const char receive_text[] = "recv evenai text_len = %d, text = %.*s";
static const char receive_short[] = "[even_ai.page]recv evenai text_len = %d, text = %.*s";
static const char no_reply_text[] = "not asked, not allow to show reply";
static const char no_reply_short[] = "[even_ai.page]not asked, not allow to show reply";
static const char no_skill_text[] = "not asked, not allow to show skills text";
static const char no_skill_short[] = "[even_ai.page]not asked, not allow to show skills text";
static const char final_text[] = "recv evenai f_text_end = %d, text_len = %d, text = %.*s";
static const char final_short[] = "[even_ai.page]recv evenai f_text_end = %d, text_len = %d, text = %.*s";
static const char stop_text[] = "stop current streaming, avoid text confusion";
static const char stop_short[] = "[even_ai.page]stop current streaming, avoid text confusion";
static const char skill_text[] = "recv evenai skill_param = %d";
static const char skill_short[] = "[even_ai.page]recv evenai skill_param = %d";

static void log_event(uint8_t severity, uint32_t line, uint32_t code,
                      const char *message, const char *short_message,
                      uint32_t a, uint32_t b, uint32_t c, const void *text) {
    if (audio_log_flags() & 2u)
        audio_log_extended(severity, log_module, log_path, log_function,
                           line, message, a, b, c, text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(code, short_message, short_message,
                                    a, b, c, text);
}

static uint16_t read16(const uint8_t *p) {
    return (uint16_t)(p[0] | ((uint16_t)p[1] << 8));
}
static uint32_t read32(const uint8_t *p) {
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) |
           ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void copy_bytes(uint8_t *dst, const uint8_t *src, uint32_t n) {
    for (uint32_t i = 0; i < n; ++i) dst[i] = src[i];
}
static void clear_bytes(uint8_t *dst, uint32_t n) {
    for (uint32_t i = 0; i < n; ++i) dst[i] = 0u;
}
static void copy_string_limit(uint8_t *dst, const uint8_t *src, uint32_t n) {
    uint32_t i = 0;
    for (; i < n && src[i] != 0u; ++i) dst[i] = src[i];
    for (; i < n; ++i) dst[i] = 0u;
}
static uint32_t string_length(const uint8_t *text) {
    uint32_t n = 0;
    while (text[n] != 0u) ++n;
    return n;
}
static uint32_t text_handle(void) {
    return audio_even_ai_text_stream_handle_20074c04;
}
static void send_byte(uint32_t no_reply, uint8_t value) {
    if (no_reply == 0u)
        audio_even_ai_display_ctrl_4e1fd2(1u, &value, 1u);
}
static void put_text(uint8_t *state, const uint8_t *event,
                     uint32_t terminate_empty) {
    uint16_t length = read16(event + 0x16u);
    state[0x0e] = (uint8_t)length;
    state[0x0f] = (uint8_t)(length >> 8);
    if (length != 0u || terminate_empty != 0u) {
        copy_bytes(state + 0x10u, event + 0x18u, length);
        if (length < 0x200u)
            state[0x10u + length] = 0u;
    }
}

void audio_even_ai_ready_4e20f2(uint32_t no_reply) {
    uint8_t *event = audio_even_ai_service_state_2006ed10;
    uint8_t *state = audio_even_ai_ready_state_2006f138;
    uint8_t action = event[1];
    uint8_t kind = event[2];
    log_event(3u, 0x86u, 0x0c800000u, action_text, action_short,
              action, kind, 0u, 0);
    if (action == 1u) {
        if (kind == 1u) {
            uint8_t reply[4] = {0u, 0u, 0u, 0u};
            audio_even_ai_state_lock_4e1fa6();
            if (event[0x13] != 0u && audio_uart_display_state[0] == 1u &&
                audio_quicklist_refresh_enabled_4434d0(7u) == 1u) {
                reply[0] = 8u;
                reply[1] = event[0x13];
                reply[2] = event[0x14];
                reply[3] = event[0x15];
            } else {
                if (audio_ux_get_system_ble_status() == 1u) {
                    (void)audio_even_ai_app_acquire_54f380(3u);
                    audio_even_ai_timer_start_all_4e31a0(5000u);
                } else {
                    event[1] = 7u;
                    event[2] = 2u;
                    audio_even_ai_timer_start_all_4e31a0(3000u);
                }
                audio_even_ai_init_text_stream_4e551e();
                audio_even_ai_stop_current_streaming_4e557c(
                    state[0] == 3u || state[0] == 4u ? 0u : 1u);
                state[0] = event[1];
                state[1] = event[2];
                reply[0] = 3u;
            }
            state[8] = (uint8_t)(audio_even_ai_config_state_20074974[1] & 0xf0u);
            state[9] = audio_even_ai_config_state_20074974[2];
            state[0x0d] = 0u;
            audio_even_ai_state_unlock_4e1fbe();
            if (no_reply == 0u) {
                if (audio_uart_display_state[0] == 1u &&
                    audio_quicklist_refresh_enabled_4434d0(7u) == 1u)
                    audio_even_ai_display_ctrl_4e1fd2(1u, reply, 4u);
                else
                    audio_even_ai_display_ctrl_4e1fd2(0u, 0, 0u);
            }
        } else if (kind == 3u) {
            state[0] = event[1];
            state[1] = event[2];
            state[0x0d] = 0u;
            if (no_reply == 0u)
                audio_even_ai_display_ctrl_4e1fd2(2u, 0, 0u);
        } else if (kind == 2u) {
            audio_even_ai_state_lock_4e1fa6();
            if (state[1] == 1u) {
                state[0] = event[1];
                state[1] = event[2];
                audio_even_ai_common_timer_stop_4e2e86();
                audio_even_ai_state_unlock_4e1fbe();
            } else {
                audio_even_ai_init_text_stream_4e551e();
                audio_even_ai_stop_current_streaming_4e557c(
                    state[0] == 3u || state[0] == 4u ? 0u : 1u);
                audio_even_ai_common_timer_stop_4e2e86();
                (void)audio_even_ai_app_acquire_54f380(3u);
                state[0] = event[1];
                state[1] = event[2];
                state[9] = audio_even_ai_config_state_20074974[2];
                state[0x0d] = 0u;
                audio_even_ai_state_unlock_4e1fbe();
                if (no_reply == 0u) {
                    if (audio_uart_display_state[0] == 1u &&
                        audio_quicklist_refresh_enabled_4434d0(7u) == 1u)
                        send_byte(0u, 3u);
                    else
                        audio_even_ai_display_ctrl_4e1fd2(0u, 0, 0u);
                }
            }
        }
        return;
    }
    if (action == 0u) return;
    if (action == 3u) {
        log_event(3u, 0x13au, 0x0cc00000u, receive_text, receive_short,
                  read16(event + 0x16u), 3u,
                  (uint32_t)(uintptr_t)(event + 0x18u), 0);
        audio_even_ai_state_lock_4e1fa6();
        audio_even_ai_timer_start_all_4e31a0(8000u);
        if (state[0] == 1u || state[0] == 4u) {
            const uint8_t *pending = (const uint8_t *)(uintptr_t)
                audio_text_stream_pending_text_552ce8(text_handle());
            uint32_t n = string_length(pending);
            if (n > 0x3ffu) n = 0x400u;
            if (pending != 0 && n != 0u) {
                copy_string_limit(audio_even_ai_text_pending_200f39b4, pending, n);
                audio_even_ai_text_pending_200f39b4[n] = 0u;
            }
        } else if (state[0] != 3u) {
            clear_bytes(audio_even_ai_text_pending_200f39b4, 0x400u);
            audio_even_ai_stop_current_streaming_4e557c(1u);
        }
        state[0] = event[1];
        state[0x0d] = 1u;
        put_text(state, event, 1u);
        clear_bytes(audio_even_ai_text_merged_200f3db4, 0x400u);
        uint32_t pending_length = string_length(audio_even_ai_text_pending_200f39b4);
        uint32_t n = pending_length;
        uint16_t event_length = read16(event + 0x16u);
        if (n < 0x3ffu && n + event_length < 0x3ffu) {
            if (n != 0u)
                copy_string_limit(audio_even_ai_text_merged_200f3db4,
                                  audio_even_ai_text_pending_200f39b4, n);
        } else {
            clear_bytes(audio_even_ai_text_pending_200f39b4, 0x400u);
            n = 0u;
        }
        if (event_length != 0u) {
            copy_string_limit(audio_even_ai_text_merged_200f3db4 + n,
                              event + 0x18u, event_length);
            audio_even_ai_text_merged_200f3db4[n + event_length] = 0u;
        }
        uint8_t interval = audio_even_ai_stream_interval_get_4e550a();
        (void)audio_text_stream_set_text_552c20(text_handle(),
            (const char *)audio_even_ai_text_merged_200f3db4, interval, 0u, 0u);
        if (n != 0u)
            (void)audio_text_stream_copy_bytes_553274(text_handle(), n & 0xffffu, 0u);
        audio_even_ai_state_unlock_4e1fbe();
        send_byte(no_reply, 3u);
    } else if (action == 4u) {
        audio_even_ai_state_lock_4e1fa6();
        state[0] = event[1];
        state[0x0d] = 1u;
        audio_even_ai_state_unlock_4e1fbe();
        send_byte(no_reply, 3u);
    } else if (action == 5u || action == 6u) {
        if (state[0x0d] == 0u) {
            log_event(2u, action == 5u ? 0x198u : 0x1cfu, 0x08000000u,
                      action == 5u ? no_reply_text : no_skill_text,
                      action == 5u ? no_reply_short : no_skill_short,
                      0u, 0u, 0u, 0);
            return;
        }
        if (action == 6u)
            log_event(3u, 0x1d3u, 0x0c400000u, skill_text, skill_short,
                      read32(event + 0x0cu), 0u, 0u, 0);
        log_event(3u, action == 5u ? 0x19du : 0x1d5u, 0x0d000000u,
                  final_text, final_short, event[0x12],
                  read16(event + 0x16u), 3u, event + 0x18u);
        audio_even_ai_state_lock_4e1fa6();
        audio_even_ai_timer_start_all_4e31a0(10000u);
        if (state[0] != action) {
            if (action == 5u)
                log_event(3u, 0x1aau, 0x0c000000u, stop_text, stop_short,
                          0u, 0u, 0u, 0);
            audio_even_ai_stop_current_streaming_4e557c(1u);
            clear_bytes(audio_even_ai_text_pending_200f39b4, 0x400u);
        }
        state[0] = event[1];
        if (action == 6u) {
            state[1] = event[2];
            copy_bytes(state + 4u, event + 0x0cu, 4u);
        }
        state[0x0c] = event[0x12];
        put_text(state, event, 0u);
        if (action == 5u && read16(state + 0x0eu) != 0u) {
            uint8_t interval = audio_even_ai_stream_interval_get_4e550a();
            (void)audio_text_stream_set_text_552c20(text_handle(),
                (const char *)(state + 0x10u), interval, 1u, 0u);
        }
        audio_even_ai_state_unlock_4e1fbe();
        if (action == 5u) {
            send_byte(no_reply, 3u);
        } else if (state[1] == 1u) {
            send_byte(no_reply, 3u);
        } else if (state[1] == 3u) {
            if (read32(state + 4u) == 1u) {
                if (no_reply == 0u)
                    audio_even_ai_display_ctrl_4e1fd2(2u, 0, 0u);
                audio_even_ai_ancc_state_sync_497cf0(4u, 500u);
            } else {
                if (read32(state + 4u) == 2u)
                    audio_even_ai_sync_remote_4973f4(1u);
                send_byte(no_reply, 3u);
            }
        } else if (state[1] == 8u) {
            send_byte(no_reply, 3u);
        } else if ((state[1] == 5u || state[1] == 6u || state[1] == 7u) &&
                   read32(state + 4u) == 0u) {
            audio_even_ai_state_lock_4e1fa6();
            uint8_t interval = audio_even_ai_stream_interval_get_4e550a();
            (void)audio_text_stream_set_text_552c20(text_handle(),
                (const char *)(state + 0x10u), interval, 1u, 0u);
            audio_even_ai_state_unlock_4e1fbe();
            send_byte(no_reply, 3u);
        }
    } else if (action == 7u) {
        audio_even_ai_state_lock_4e1fa6();
        audio_even_ai_timer_start_all_4e31a0(3000u);
        if (state[0] != 7u)
            clear_bytes(audio_even_ai_text_pending_200f39b4, 0x400u);
        state[0] = event[1];
        state[1] = event[2];
        audio_even_ai_state_unlock_4e1fbe();
        send_byte(no_reply, 3u);
    }
}
