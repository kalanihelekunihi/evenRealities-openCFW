/* Apollo s200 2.2.6.10 terminal cells transcribed from authenticated literals.
 * Cluster v2 supersedes the two separate Terminal field sections in terminal_ram_placement.ld.
 * Include this fragment in a final image linker only after the full RAM map is
 * checked for overlap. It covers twenty-three storage sections plus ten aliases in the Terminal block;
 * two buffer spans and the manager record have only proven minimum extents. */
SECTIONS {
  .g2.ram.system_alert_page_id 0x20003bcc (NOLOAD) : {
    KEEP(*(.g2.ram.system_alert_page_id))
  }
  .g2.ram.settings_manager_storage 0x200036fc (NOLOAD) : {
    KEEP(*(.g2.ram.settings_manager_storage))
  }
  .bss.opencfw.terminal.ui_state 0x2006e0d0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.ui_state))
  }
  .g2.ram.settings_notify_encode_buffer 0x200706ec (NOLOAD) : {
    KEEP(*(.g2.ram.settings_notify_encode_buffer))
  }
  .g2.ram.settings_notify_staging 0x200725a0 (NOLOAD) : {
    KEEP(*(.g2.ram.settings_notify_staging))
  }
  .g2.ram.settings_last_message_state 0x20072608 (NOLOAD) : {
    KEEP(*(.g2.ram.settings_last_message_state))
  }
  .g2.ram.settings_config_live 0x20072da8 (NOLOAD) : {
    KEEP(*(.g2.ram.settings_config_live))
  }
  .g2.ram.settings_notify_magic 0x2007486c (NOLOAD) : {
    KEEP(*(.g2.ram.settings_notify_magic))
  }
  .g2.ram.system_alert_font 0x200746e0 (NOLOAD) : {
    KEEP(*(.g2.ram.system_alert_font))
  }
  .g2.ram.settings_ancc_mutex 0x2007491c (NOLOAD) : {
    KEEP(*(.g2.ram.settings_ancc_mutex))
  }
  .g2.ram.settings_left_version_last_request_tick 0x20074994 (NOLOAD) : {
    KEEP(*(.g2.ram.settings_left_version_last_request_tick))
  }
  .g2.ram.settings_peer_send_queue 0x200749cc (NOLOAD) : {
    KEEP(*(.g2.ram.settings_peer_send_queue))
  }
  .g2.ram.system_alert_parent 0x200749ec (NOLOAD) : {
    KEEP(*(.g2.ram.system_alert_parent))
  }
  .g2.ram.system_alert_child 0x200749f0 (NOLOAD) : {
    KEEP(*(.g2.ram.system_alert_child))
  }
  .g2.ram.system_alert_message_notify 0x200749f4 (NOLOAD) : {
    KEEP(*(.bss.g2.ram.system_alert_message_notify))
  }
  .g2.ram.settings_peer_event 0x20074b10 (NOLOAD) : {
    KEEP(*(.g2.ram.settings_peer_event))
  }
  .g2.ram.terminal_message_sequence 0x20074fff (NOLOAD) : {
    KEEP(*(.g2.ram.terminal_message_sequence))
  }
  .g2.ram.settings_ancc_count 0x2007500d (NOLOAD) : {
    KEEP(*(.g2.ram.settings_ancc_count))
  }
  .g2.ram.silent_mode_ui_status 0x2007501d (NOLOAD) : {
    KEEP(*(.g2.ram.silent_mode_ui_status))
  }
  .g2.ram.silent_mode_change_from_app 0x2007501e (NOLOAD) : {
    KEEP(*(.g2.ram.silent_mode_change_from_app))
  }
  .g2.ram.system_alert_active 0x20075025 (NOLOAD) : {
    KEEP(*(.g2.ram.system_alert_active))
  }
  .g2.ram.terminal_tx_staging 0x200f9694 (NOLOAD) : {
    KEEP(*(.g2.ram.terminal_tx_staging))
  }
  .g2.ram.terminal_tx_encoded 0x20374378 (NOLOAD) : {
    KEEP(*(.g2.ram.terminal_tx_encoded))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2.ram.system_alert_page_id) == 4, "system alert page id size")
ASSERT(SIZEOF(.g2.ram.settings_manager_storage) == 0x20, "settings manager minimum size")
ASSERT(SIZEOF(.bss.opencfw.terminal.ui_state) == 0x2a0, "terminal UI state cluster size")
ASSERT(audio_terminal_agent_session_ptr == audio_terminal_ui_state_base + 0x004, "terminal session pointer offset")
ASSERT(audio_terminal_mode_sync_pending == audio_terminal_ui_state_base + 0x274, "terminal mode sync offset")
ASSERT(audio_terminal_ui_mode == audio_terminal_ui_state_base + 0x275, "terminal mode offset")
ASSERT(audio_terminal_runtime_flag_277 == audio_terminal_ui_state_base + 0x277, "terminal runtime flag 277 offset")
ASSERT(audio_terminal_selector_loading == audio_terminal_ui_state_base + 0x27d, "terminal selector loading offset")
ASSERT(audio_terminal_runtime_flag_27f == audio_terminal_ui_state_base + 0x27f, "terminal runtime flag 27f offset")
ASSERT(audio_terminal_runtime_saved_session == audio_terminal_ui_state_base + 0x288, "terminal saved session offset")
ASSERT(audio_terminal_agent_special_flag == audio_terminal_ui_state_base + 0x28c, "terminal special flag offset")
ASSERT(audio_terminal_output_tracking == audio_terminal_ui_state_base + 0x294, "terminal output tracking offset")
ASSERT(audio_terminal_session_switch_tick == audio_terminal_ui_state_base + 0x29c, "terminal switch tick offset")
ASSERT(SIZEOF(.g2.ram.settings_notify_encode_buffer) == 0x100, "settings encode buffer size")
ASSERT(SIZEOF(.g2.ram.settings_notify_staging) == 0x68, "settings staging size")
ASSERT(SIZEOF(.g2.ram.settings_last_message_state) == 0x68, "settings last-message minimum size")
ASSERT(SIZEOF(.g2.ram.settings_config_live) == 0x50, "settings live config minimum size")
ASSERT(SIZEOF(.g2.ram.settings_notify_magic) == 4, "settings sequence size")
ASSERT(SIZEOF(.g2.ram.system_alert_font) == 4, "system alert font size")
ASSERT(SIZEOF(.g2.ram.settings_ancc_mutex) == 4, "settings ANCC mutex size")
ASSERT(SIZEOF(.g2.ram.settings_left_version_last_request_tick) == 4, "settings left version tick size")
ASSERT(SIZEOF(.g2.ram.settings_peer_send_queue) == 4, "settings peer queue size")
ASSERT(SIZEOF(.g2.ram.system_alert_parent) == 4, "system alert parent size")
ASSERT(SIZEOF(.g2.ram.system_alert_child) == 4, "system alert child size")
ASSERT(SIZEOF(.g2.ram.system_alert_message_notify) == 4, "system alert mode size")
ASSERT(SIZEOF(.g2.ram.settings_peer_event) == 4, "settings peer event size")
ASSERT(SIZEOF(.g2.ram.terminal_message_sequence) == 1, "terminal sequence size")
ASSERT(SIZEOF(.g2.ram.settings_ancc_count) == 1, "settings ANCC count size")
ASSERT(SIZEOF(.g2.ram.silent_mode_ui_status) == 1, "silent mode UI status size")
ASSERT(SIZEOF(.g2.ram.silent_mode_change_from_app) == 1, "silent mode app change size")
ASSERT(SIZEOF(.g2.ram.system_alert_active) == 1, "system alert active size")
ASSERT(SIZEOF(.g2.ram.terminal_tx_staging) == 0x850, "terminal staging size")
ASSERT(SIZEOF(.g2.ram.terminal_tx_encoded) == 0x878, "terminal encoded size")
