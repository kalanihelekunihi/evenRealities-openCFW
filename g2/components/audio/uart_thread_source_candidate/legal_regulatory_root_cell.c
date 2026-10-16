/* The stock legal page builder writes one word through its literal pointer
 * at 0x5bf8a4 -> RAM 0x200746a4. Allocation extent beyond that word and
 * final RAM placement remain to be proved. */
#include <stdint.h>

uint32_t audio_legal_regulatory_root_200746a4;
