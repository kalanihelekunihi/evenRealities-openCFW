/* Preserve the existing fixed RAM sections and add the response spans. */
INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_sync_info_common_472102.ld"
SECTIONS {
  .g2_sync_info_response_200740c8 0x200740c8 (NOLOAD) : {
    KEEP(*(.g2_sync_info_response_200740c8))
  }
  .g2_sync_info_encode_buffer_20071c48 0x20071c48 (NOLOAD) : {
    KEEP(*(.g2_sync_info_encode_buffer_20071c48))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_sync_info_response_200740c8) == 12, "response size")
ASSERT(SIZEOF(.g2_sync_info_encode_buffer_20071c48) == 128, "encode buffer size")
ASSERT(audio_sync_info_response_200740c8 == 0x200740c8, "response address")
ASSERT(audio_sync_info_encode_buffer_20071c48 == 0x20071c48, "encode address")
