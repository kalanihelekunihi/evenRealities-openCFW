/* Native hand-state checksum commit 0x466016. Literal 0x4667ec resolves
 * 0x200736d4; 0x4667f0 resolves settings-manager struct RAM 0x200036fc. */
#include <stdint.h>
extern uint8_t audio_uart_hand_record[0x30u]; /* RAM 0x200736d4 */
extern uint8_t audio_uart_hand_snapshot_context[]; /* RAM struct base 0x200036fc */
extern uint16_t audio_uart_hand_checksum_49acd4(const void *,uint32_t,const uint16_t *);
extern void audio_uart_hand_mismatch_448e34(void); /* native failure control */
void audio_uart_ring_unpair_commit_hand_466016(void) {
    const uint8_t *snapshot=audio_uart_hand_snapshot_context;
    const uint8_t *record=audio_uart_hand_record;
    const uint8_t *snapshot_first=*(const uint8_t *const *)(const void *)(snapshot+0x14u);
    uint16_t first=audio_uart_hand_checksum_49acd4(record,0x12u,0);
    *(uint16_t *)(void *)(audio_uart_hand_record+0x12u)=first;
    uint16_t old_first=*(const uint16_t *)(const void *)(snapshot_first+0x12u);
    const uint8_t *snapshot_second=*(const uint8_t *const *)(const void *)(snapshot+0x0cu);
    uint16_t second=audio_uart_hand_checksum_49acd4(record+0x14u,8u,0);
    *(uint16_t *)(void *)(audio_uart_hand_record+0x1cu)=second;
    uint16_t old_second=*(const uint16_t *)(const void *)(snapshot_second+8u);
    const uint8_t *snapshot_third=*(const uint8_t *const *)(const void *)(snapshot+0x10u);
    uint16_t third=audio_uart_hand_checksum_49acd4(record+0x20u,8u,0);
    *(uint16_t *)(void *)(audio_uart_hand_record+0x28u)=third;
    if(*(const uint16_t *)(const void *)(snapshot_third+8u)!=third ||
       old_second!=second || old_first!=first)
        audio_uart_hand_mismatch_448e34();
}
