/* Fault-code message lookup used by APP_errorFaultHandler (stock 0x509b48,
 * search loop 0x509b64..0x509b80).
 *
 * Stock searches the 43-row table at ROM 0x6c8e60 with a uint8_t index and
 * no bound (rows 43..255 are whatever ROM follows the table). In the stock
 * image all 103 call sites of 0x509b48 build the record from a ROM template
 * with type 0, detail 1, so the code is always 0x0001 and the search stops
 * at row 1 (checked by scanning every `bl 0x509b48` in the 2.2.6.10 image,
 * evidence g2-20261122-ws-app-fault-lookup.json). The rows past the table are
 * never reached by stock code, so they are not carried here: the search wraps
 * over the 43 real rows instead. Every code that is in the table gives the
 * same row as stock.
 *
 * Verified against stock on Renode 1.17 M55 (spec fault-a). */
#include <stdint.h>

struct audio_fault_code_row { uint16_t code, reserved; const char *message; };
_Static_assert(sizeof(struct audio_fault_code_row) == 8u, "fault row ABI");
#define AUDIO_FAULT_CODE_ROWS 43u
extern const struct audio_fault_code_row audio_fault_code_table[AUDIO_FAULT_CODE_ROWS];

const char *audio_fault_code_message(uint16_t code) {
    uint32_t index = 0u;
    while (audio_fault_code_table[index].code != code)
        index = index + 1u < AUDIO_FAULT_CODE_ROWS ? index + 1u : 0u;
    return audio_fault_code_table[index].message;
}
