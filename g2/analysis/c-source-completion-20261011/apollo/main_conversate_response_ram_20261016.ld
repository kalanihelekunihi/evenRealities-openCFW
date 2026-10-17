INCLUDE "g2/analysis/c-source-completion-20261011/apollo/main_conversate_action_mutex_20074398.ld"
SECTIONS {
  .g2_conversate_response_frame_200f4808 0x200f4808 (NOLOAD) : {
    KEEP(*(.g2_conversate_response_frame_200f4808))
  }
  .g2_conversate_response_encoded_2037c2a0 0x2037c2a0 (NOLOAD) : {
    KEEP(*(.g2_conversate_response_encoded_2037c2a0))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.g2_conversate_response_frame_200f4808) == 4012,
       "Conversate response frame size")
ASSERT(SIZEOF(.g2_conversate_response_encoded_2037c2a0) == 256,
       "Conversate encoded buffer size")
ASSERT(audio_conversate_response_frame_200f4808 == 0x200f4808,
       "Conversate frame address")
ASSERT(audio_conversate_response_encoded_2037c2a0 == 0x2037c2a0,
       "Conversate encoded buffer address")
