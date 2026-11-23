#include "blob_read.h"
_Static_assert(sizeof(g2_blob)==20,"ARM blob size");
_Static_assert(__builtin_offsetof(g2_blob,saved_len)==16,"saved length offset");
/* Stock 0x54116E (SVC_FlashDBBlobRead) */
/* KNOWN UPSTREAM/STOCK BUG, kept deliberately for fidelity to stock 2.2.6.10:
 * g2_flashdb_candidate_get_blob is upstream FlashDB 2.1.1 fdb_kv_get_blob (stock 0x54454a). With
 * FDB_KV_USING_CACHE, find_kv() returns true on a KV-cache hit even when read_kv() then fails
 * (CRC32 mismatch or bad length header), so get_kv() reads the value from kv.addr.value with
 * kv.value_len, both uninitialised. The stock image has the same behaviour (Renode differential:
 * stock read address 0x544fed, C 0xf, both stack garbage). It only triggers after flash corruption
 * of a cached KV; the returned length and blob.saved_len are then garbage-derived.
 * Evidence: g2/evidence/g2-20261122-ws-blestore-fdb-core.json. */
uint32_t g2_flashdb_candidate_blob_read(uint32_t index,uint32_t key,uint32_t buf,uint32_t length) {
    g2_blob blob;
    g2_flashdb_candidate_tick();
    blob.buf=buf;
    blob.size=length & 0xffffu;
    uint32_t result=g2_flashdb_candidate_get_blob(g2_flashdb_candidate_literals[0]+(index&255u)*2220u,key,&blob);
    if (blob.saved_len==0) {
        if (g2_flashdb_candidate_flags() & 2u)
            g2_flashdb_candidate_log(1,g2_flashdb_candidate_literals[1],g2_flashdb_candidate_literals[2],g2_flashdb_candidate_literals[3],241,g2_flashdb_candidate_literals[4],key,result);
        if ((g2_flashdb_candidate_flags() & 1u) || (g2_flashdb_candidate_flags() & 4u))
            g2_flashdb_candidate_compress(0x4800000,g2_flashdb_candidate_literals[5],g2_flashdb_candidate_literals[5],key,result);
    }
    g2_flashdb_candidate_tick();
    return result;
}
