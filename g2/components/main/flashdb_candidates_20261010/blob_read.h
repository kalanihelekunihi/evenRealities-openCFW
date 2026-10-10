#ifndef G2_CANDIDATE_BLOB_READ_H
#define G2_CANDIDATE_BLOB_READ_H
#include <stdint.h>
/* ARM32 contract. Provider must initialize saved_len before returning. */
typedef struct { uint32_t buf, size, saved_meta[2], saved_len; } g2_blob;
extern uint32_t g2_flashdb_candidate_tick(void);
extern uint32_t g2_flashdb_candidate_get_blob(uint32_t db, uint32_t key, g2_blob *blob);
extern uint32_t g2_flashdb_candidate_flags(void);
extern void g2_flashdb_candidate_log(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern void g2_flashdb_candidate_compress(uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
extern const uint32_t g2_flashdb_candidate_literals[7];
uint32_t g2_flashdb_candidate_blob_read(uint32_t index,uint32_t key,uint32_t buf,uint32_t length);
#endif
