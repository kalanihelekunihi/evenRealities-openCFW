#include "blob_read.h"
volatile uint32_t trace[80], used, flag_value, payload_len;
volatile unsigned char payload[32];
const uint32_t g2_flashdb_candidate_literals[7]={0}; /* replaced with authenticated data at oracle load */
static void record(uint32_t x) { trace[used++]=x; }
uint32_t g2_flashdb_candidate_tick(void) { record(1); return used; }
uint32_t g2_flashdb_candidate_flags(void) { record(2); return flag_value; }
uint32_t g2_flashdb_candidate_get_blob(uint32_t db,uint32_t key,g2_blob *b) {
    record(3); record(db); record(key); record(b->buf); record(b->size);
    uint32_t n=b->size<payload_len?b->size:payload_len;
    for(uint32_t i=0;i<n;i++) ((unsigned char *)(uintptr_t)b->buf)[i]=payload[i];
    b->saved_len=payload_len;
    return n;
}
void g2_flashdb_candidate_log(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g,uint32_t h) {
    record(4);record(a);record(b);record(c);record(d);record(e);record(f);record(g);record(h);
}
void g2_flashdb_candidate_compress(uint32_t a,uint32_t b,uint32_t c,uint32_t d,uint32_t e) {
    record(5);record(a);record(b);record(c);record(d);record(e);
}
