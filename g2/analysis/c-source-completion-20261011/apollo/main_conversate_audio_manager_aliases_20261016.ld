/* Conversate's two calls target the same native audio-manager bodies already
   compiled under their audio-manager provider names. */
SECTIONS { .g2_conversate_audio_manager_aliases : { } }
INSERT AFTER .bss;
audio_conversate_page_show_54f380 = audio_even_ai_app_acquire_54f380;
audio_conversate_page_hide_54f50e = audio_terminal_reset_mode_notice_54f50e;
ASSERT(audio_conversate_page_show_54f380 == audio_even_ai_app_acquire_54f380,
       "Conversate app acquire target")
ASSERT(audio_conversate_page_hide_54f50e == audio_terminal_reset_mode_notice_54f50e,
       "Conversate app release target")
