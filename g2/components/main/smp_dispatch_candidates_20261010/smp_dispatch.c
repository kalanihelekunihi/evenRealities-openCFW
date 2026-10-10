#include "smp_dispatch.h"
static uint32_t word(const uint8_t *p) {
  return (uint32_t)p[0] | (uint32_t)p[1]<<8 | (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
static void stale_log(const uint8_t *m, const uint8_t *c,
                      const g2_smp_literals *l, const g2_smp_providers *p) {
  uint32_t carry = 0;
  /* Each call receives the actual preceding r0 value, including comparison
   * failures; repeated gates in the stock body have no r0 reload. */
  for (uint32_t level = 1; level <= 4; ++level) {
    carry = p->log_gate(p->context, carry);
    if (!carry) continue;
    if (level < 4) {
      uint32_t rhs = level == 1 ? 0x537eb4u : level == 2 ? l->category : l->comparison3;
      carry = p->compare(p->context, l->category, rhs, level == 1 ? 3u : 4u);
      if (carry) continue;
    }
    if (p->log_flags(p->context) & 2u)
      p->log_extended(p->context, level, 0x537eb8u, l->source, l->file,
                      885u, l->format, c[65], m[3]);
    return;
  }
  carry = p->log_gate(p->context, carry);
  if (carry && !p->compare(p->context, 0x537eb8u, 0x537ec0u, 3u)) return;
  p->log_fallback(p->context, l->category, l->format, c[65], m[3]);
}
void g2_candidate_smp_handler(uint8_t event, const uint8_t *m,
                              const g2_smp_literals *l, const g2_smp_providers *p) {
  (void)event;
  if (!m) return;
  if (m[2] == 32u) { p->database_service(p->context); return; }
  if (m[2] == 28u && word(m+8)) p->buffer_free(p->context, word(m+8));
  const uint8_t *c = p->ccb_by_id(p->context, m[0]);
  if (!c[61]) return;
  if (m[2] != 11u || c[65] == m[3]) {
    p->state_machine(p->context, c, m); return;
  }
  uint8_t handler_id = 0;
  stale_log(m, c, l, p);
  uint32_t buffer;
  while ((buffer = p->message_dequeue(p->context, l->aes_queue, &handler_id)) != 0)
    p->message_free(p->context, buffer);
}
