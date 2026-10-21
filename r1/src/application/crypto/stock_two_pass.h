#ifndef R1_STOCK_TWO_PASS_H
#define R1_STOCK_TWO_PASS_H
#include <stdint.h>
/* Stock XOR helper 0x98E22. Negative length performs no accesses. */
void r1_stock_xor(uint8_t *output, const uint8_t *chain, int32_t length);
/* Stock 0x48B02. For supported calls: length is nonnegative; input/output
 * are disjoint, readable/writable for length bytes; both keys have 16 bytes;
 * keys and output length storage do not overlap the buffers. Complete blocks
 * are transformed; any partial trailing block remains copied verbatim.
 * No new validation, padding, or altered failure policy is introduced. */
void r1_stock_two_pass(const uint8_t *input, int32_t length,
                      const uint8_t second_key[16], const uint8_t first_key[16],
                      uint8_t *output, int32_t *output_length);
/* Stock 0x891A4: first_key=key[0:16], second_key=key[16:32]; returns zero. */
uint32_t r1_stock_two_pass_callback(const uint8_t *input, int32_t length,
                                  const uint8_t key[32], uint8_t *output,
                                  int32_t *output_length);
#endif
