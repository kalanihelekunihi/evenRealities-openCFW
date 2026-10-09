/* Corrected analysis-only scheduler continuation, not a firmware replacement.
 * Candidate-producing operation remains opaque; 0x311644 narrows r13 to byte.
 */
#include <stdint.h>
/* Assertion continuation and nextPrio storage are caller-supplied boundaries. */
unsigned scheduler_tail(uint32_t candidate,unsigned active,unsigned lock) {
 unsigned p=(uint8_t)candidate;
 if(p <= (uint8_t)active || p <= (uint8_t)lock) return 0;
 if(p >= 17) assert_3117d8(0x33451c,410);
 nextPrio=(uint8_t)candidate;
 return (uint8_t)candidate;
}
