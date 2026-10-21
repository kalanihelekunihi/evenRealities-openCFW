#include <stdint.h>

extern const uint8_t *audio_ble_comm_profile_slot;
extern uint32_t audio_ble_link_mask_select_47ae78(uint32_t, uint8_t, uint8_t *);
extern const uint8_t *DmConnPeerAddr(uint8_t);
extern uint8_t DmConnPeerAddrType(uint8_t);
extern uint8_t *audio_ble_pair_record_create_47a71c(uint8_t, const uint8_t *, uint8_t);
extern void audio_ble_vendor_link_activate_55bc1e(uint8_t, uint8_t, uint32_t);
extern void audio_ble_vendor_link_start_55bbea(uint8_t, uint8_t, uint8_t, uint8_t, uint8_t);

/* Native 0x503498. The two vendor calls retain their original entry
 * identities until their bodies and timing are reduced separately. */
void audio_ble_master_row_dispatch_503498(uint32_t connection, uint32_t mode,
                                          void *record)
{
    uint8_t conn = (uint8_t)connection;
    uint8_t selected_mode = (uint8_t)mode;
    volatile uint8_t *row = (volatile uint8_t *)record;
    uint32_t handle = *(volatile uint32_t *)record;
    if (handle != 0u) {
        uint8_t selected = 0u;
        uint32_t link = audio_ble_link_mask_select_47ae78(handle, 2u, &selected);
        if (link != 0u) {
            row[6] = 1u;
            row[8] = 1u;
            audio_ble_vendor_link_activate_55bc1e(conn, selected, link);
            return;
        }
    }
    if (selected_mode == 0u)
        return;
    const uint8_t *profile = audio_ble_comm_profile_slot;
    row[7] = (uint8_t)(profile[0] & 1u);
    if (row[7] != 0u && handle == 0u) {
        const uint8_t *address = DmConnPeerAddr(conn);
        uint8_t type = DmConnPeerAddrType(conn);
        uint8_t *created = audio_ble_pair_record_create_47a71c(type, address, 1u);
        *(volatile uint32_t *)record = (uint32_t)(uintptr_t)created;
    }
    row[11] = 0u;
    uint8_t flags = profile[2];
    if (DmConnPeerAddrType(conn) == 1u)
        flags = (uint8_t)(flags | 2u);
    row[8] = 1u;
    audio_ble_vendor_link_start_55bbea(conn, profile[3], profile[0],
                                       profile[1], flags);
}
