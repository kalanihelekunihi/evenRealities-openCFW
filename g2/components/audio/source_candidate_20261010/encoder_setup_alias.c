/* The original diagnostic import 0x57a927 is the reset-config entry already
 * reconstructed and executed in encoder_setup_offline/setup.c. Export its
 * caller name at the same entry, with no wrapper call or extra state write. */
#include "../encoder_setup_offline/setup.c"

__asm__(".global audio_encoder_setup\n"
        ".set audio_encoder_setup, audio_encoder_reset_config\n");
