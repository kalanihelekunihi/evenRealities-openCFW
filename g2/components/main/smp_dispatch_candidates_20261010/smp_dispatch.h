#ifndef G2_SMP_DISPATCH_CANDIDATE_H
#define G2_SMP_DISPATCH_CANDIDATE_H
#include <stdint.h>
/* Host pointers carry readable message/CCB storage. Firmware pointer words
 * remain uint32_t and are resolved by providers, never cast to host pointers. */
typedef struct {
  uint32_t category, comparison3, source, format, file, aes_queue;
} g2_smp_literals;
typedef struct {
  void *context;
  void (*database_service)(void *);
  void (*buffer_free)(void *, uint32_t);
  const uint8_t *(*ccb_by_id)(void *, uint8_t);
  void (*state_machine)(void *, const uint8_t *, const uint8_t *);
  uint32_t (*log_gate)(void *, uint32_t);
  uint32_t (*compare)(void *, uint32_t, uint32_t, uint32_t);
  uint32_t (*log_flags)(void *);
  void (*log_extended)(void *, uint32_t, uint32_t, uint32_t, uint32_t,
                       uint32_t, uint32_t, uint32_t, uint32_t);
  void (*log_fallback)(void *, uint32_t, uint32_t, uint32_t, uint32_t);
  uint32_t (*message_dequeue)(void *, uint32_t, uint8_t *);
  void (*message_free)(void *, uint32_t);
} g2_smp_providers;
void g2_candidate_smp_handler(uint8_t event, const uint8_t *message,
                              const g2_smp_literals *, const g2_smp_providers *);
#endif
