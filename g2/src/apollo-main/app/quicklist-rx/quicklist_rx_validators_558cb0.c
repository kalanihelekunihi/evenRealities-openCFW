/* QuickList receive validators at 0x558cb0, 0x558f34 and 0x559378. NULL-payload
 * assert records point at this unit's own path/function strings (stock pointed at
 * its copies: 0x6db358 path, 0x78231c / 0x77a5ac / 0x782330 function names). */
#include <stdint.h>

/* APP_errorFaultHandler record (app/fault-handler/fault_handler_509b48.c). */
struct audio_fault_record {
    uint32_t type, detail;
    const char *path, *function;
    uint32_t line;
};
_Static_assert(sizeof(struct audio_fault_record) == 20u, "fault record ABI");

extern void audio_uart_checksum_copy(void *, const void *, uint32_t);
extern void audio_ring_pb_assert_509b48(const struct audio_fault_record *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "pb.quicklist";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\pb_service_quicklist\\pb_service_quicklist.c";
static void assert_null(const char *function, uint32_t line) {
    const struct audio_fault_record record = { 0u, 1u, path, function, line };
    audio_ring_pb_assert_509b48(&record);
}

/* Stock 0x558CB0 (PB_RxQuicklistItem) */
uint32_t audio_quicklist_one_validate(uint32_t id, const void *payload) {
    (void)id;
    if (payload == 0) {
        assert_null("PB_RxQuicklistItem", 151u);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, "PB_RxQuicklistItem", 0x99u, "POINTER NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]POINTER NULL", "[pb.quicklist]POINTER NULL");
        return 2u;
    }
    const uint8_t *p = (const uint8_t *)payload;
    /* int64 timestamp at +0x10: stock passes it 8-byte aligned (ldrd/strd), so the
     * compressed log gets a padding slot before it (AAPCS variadic long long). */
    const int64_t timestamp = (int64_t)(((uint64_t)*(const uint32_t *)(p + 20u) << 32) |
                                        *(const uint32_t *)(p + 16u));
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, "PB_RxQuicklistItem", 0x9eu,
                           "pItem:uid = %d, index = %d, isCompleted = %d, title.size = %d, timestamp = %lld, ts_type = %d",
                           *(const uint32_t *)(p + 0u), *(const uint32_t *)(p + 4u),
                           *(const uint32_t *)(p + 8u), (uint32_t)p[24] | ((uint32_t)p[25] << 8),
                           timestamp, p[0xe5u]);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x11800000u,
                                    "[pb.quicklist]pItem:uid = %d, index = %d, isCompleted = %d, title.size = %d, timestamp = %lld, ts_type = %d",
                                    "[pb.quicklist]pItem:uid = %d, index = %d, isCompleted = %d, title.size = %d, timestamp = %lld, ts_type = %d",
                                    *(const uint32_t *)(p + 0u), *(const uint32_t *)(p + 4u),
                                    *(const uint32_t *)(p + 8u), (uint32_t)p[24] | ((uint32_t)p[25] << 8),
                                    timestamp, p[0xe5u]);
    return 0u;
}

/* Stock 0x558F34 (PB_RxQuicklistMultItems) */
uint32_t audio_quicklist_many_validate(uint32_t id, const void *payload) {
    (void)id;
    if (payload == 0) {
        assert_null("PB_RxQuicklistMultItems", 240u);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, "PB_RxQuicklistMultItems", 0xf2u, "POINTER NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]POINTER NULL", "[pb.quicklist]POINTER NULL");
        return 2u;
    }
    const uint8_t *p = (const uint8_t *)payload;
    uint32_t count = (uint32_t)p[2] | ((uint32_t)p[3] << 8);
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, "PB_RxQuicklistMultItems", 0xf7u,
                           "pMultItems:data_type = %d, total_count = %d, items_count = %d",
                           p[0], p[1], count);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10c00000u,
                                    "[pb.quicklist]pMultItems:data_type = %d, total_count = %d, items_count = %d",
                                    "[pb.quicklist]pMultItems:data_type = %d, total_count = %d, items_count = %d",
                                    p[0], p[1], count);
    return 0u;
}

/* Stock 0x559378 (PB_RxQuicklistEvent) */
uint32_t audio_quicklist_event_validate(uint32_t id, const void *payload) {
    (void)id;
    if (payload == 0) {
        assert_null("PB_RxQuicklistEvent", 331u);
        if (audio_log_flags() & 2u)
            audio_log_extended(1u, module, path, "PB_RxQuicklistEvent", 0x14du, "POINTER NULL");
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x04000000u, "[pb.quicklist]POINTER NULL", "[pb.quicklist]POINTER NULL");
        return 2u;
    }
    const uint8_t *p = (const uint8_t *)payload;
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, path, "PB_RxQuicklistEvent", 0x151u,
                           "pEventInfo:event = %d, uid = %d", p[0], *(const uint32_t *)(p + 4u));
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10800000u,
                                    "[pb.quicklist]pEventInfo:event = %d, uid = %d",
                                    "[pb.quicklist]pEventInfo:event = %d, uid = %d",
                                    p[0], *(const uint32_t *)(p + 4u));
    return 0u;
}
