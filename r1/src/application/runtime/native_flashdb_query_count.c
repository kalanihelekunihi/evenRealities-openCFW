#include <stdint.h>
#include <stdbool.h>
struct fdb_tsdb;struct fdb_tsl;
extern void r1_health_sync_provider_00063ad8(struct fdb_tsdb *,int32_t,int32_t,
                                           bool (*)(struct fdb_tsl *,void *),void *);
extern int r1_native_printf(const char *,...);
bool r1_fdb_native_query_count_cb(struct fdb_tsl *,void *);
void *r1_fdb_native_db_path(const volatile uint8_t *);
typedef struct __attribute__((packed,may_alias)) {uint32_t value;} query_word;
static uint32_t query_word_at(const volatile uint8_t *p)
{return ((const volatile query_word *)p)->value;}
/* Stock 0x63cb4 fully initializes the eight-byte callback context. Private
 * saved argument restoration is not an input/output of this C interface. */
__attribute__((section(".text.r1_fdb_native_query_count")))
uint32_t r1_health_sync_provider_00063cb4(const volatile uint8_t *db,
                                        int32_t from,int32_t to,uint32_t status)
{
 volatile uint32_t context[2]={(uint8_t)status,0};
 if (db[24]) {
  r1_health_sync_provider_00063ad8((struct fdb_tsdb *)(uintptr_t)db,from,to,
                   r1_fdb_native_query_count_cb,(void *)(uintptr_t)context);
  return context[1];
 }
 (void)r1_native_printf("[FlashDB][tsl]");
 void *path=r1_fdb_native_db_path(db);
 (void)r1_native_printf("[%s][%s] ",(const char *)(uintptr_t)query_word_at(db),path);
 (void)r1_native_printf("Error: TSL (%s) isn't initialize OK.\n",
                       (const char *)(uintptr_t)query_word_at(db));
 return 0;
}
/* Native 0x87428 reads both status bytes before touching the count word.
 * Packed volatile views preserve unaligned reads and aliased callback state. */
typedef struct __attribute__((packed,may_alias)) { uint32_t value; } r1_fdb_query_word;
bool r1_fdb_native_query_count_cb(struct fdb_tsl *entry,void *argument)
{
    const volatile uint8_t *record=(const volatile uint8_t *)entry;
    volatile uint8_t *context=(volatile uint8_t *)argument;
    uint32_t status = record[0];
    uint32_t requested = context[0];
    if (status == requested) {
        volatile r1_fdb_query_word *count = (volatile r1_fdb_query_word *)(context+4);
        count->value = count->value + 1u;
    }
    return 0;
}
/* Native 0x3f014 returns partition +4 without dereferencing that name.
 * FILE_MODE is a whole byte, not only bit zero. */
void *r1_fdb_native_db_path(const volatile uint8_t *db)
{
    if (db[25]) return 0;
    uint32_t partition = ((const volatile r1_fdb_query_word *)(db+8))->value;
    return (void *)((uintptr_t)partition + 4u);
}
