/* Cordio dmScanPhyToIdx / DmScanPhyToIdx at stock Main 0x4d2b00/0x4d2b3e. */
#include <stdint.h>

uint8_t audio_ble_dm_scan_phy_to_idx_4d2b00(uint8_t num_phys,
                                               uint8_t scan_phy)
{
    if (num_phys == 1u)
        return 0u;
    if (num_phys == 2u)
        return scan_phy == 1u ? 0u : 1u;
    if (scan_phy == 1u)
        return 0u;
    if (scan_phy == 2u)
        return 1u;
    return 2u;
}

uint8_t audio_ble_dm_scan_phy_index_4d2b3e(uint8_t scan_phy)
{
    return audio_ble_dm_scan_phy_to_idx_4d2b00(2u, scan_phy);
}
