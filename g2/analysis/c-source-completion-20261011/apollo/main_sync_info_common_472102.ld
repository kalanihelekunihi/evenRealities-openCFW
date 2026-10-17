/* Keep prior fixed RAM sections while adding the observed SyncInfo state. */
INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_extended_log_fatal_hook_alias_2007456c.ld"
SECTIONS {
  .g2_sync_info_state_200740bc 0x200740bc (NOLOAD) : {
    KEEP(*(.g2_sync_info_state_200740bc))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_sync_info_state_200740bc) == 12,
       "SyncInfo decoded state size")
ASSERT(audio_sync_info_state_200740bc == 0x200740bc,
       "SyncInfo decoded state RAM address")
