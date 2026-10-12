/* Native 0x480874 radio register and hardware identifier readout. */
#include <stdint.h>

/* Indexed native ROM tables 0x78c97c and 0x774bac, exact bounded extents. */
static const uint16_t audio_ble_radio_identifier_mode_table_78c97c[4] =
    {0x400u,0x800u,0xc00u,0x1000u};
static const uint16_t audio_ble_radio_identifier_triple_table_774bac[12] =
    {0x80u,0x100u,0x400u,0x80u,0x100u,0x800u,
     0x100u,0x200u,0x800u,0x100u,0x200u,0xc00u};
extern void audio_ble_hci_boot_delay_491102(uint32_t);

void audio_ble_hci_radio_identifier_details_480874(void *output)
{
    uint32_t *word=(uint32_t *)output;
    volatile const uint32_t *const regs=(volatile const uint32_t *)0x40020000u;
    for (unsigned i=0;i<6u;++i) word[i]=regs[i];
    word[6u]=1u;
    uint32_t mode=regs[5u];
    word[11u]=(uint32_t)audio_ble_radio_identifier_mode_table_78c97c[(mode&15u)>>2u]<<10u;
    unsigned triple=(mode&3u)*3u;
    word[8u]=(uint32_t)audio_ble_radio_identifier_triple_table_774bac[triple]<<10u;
    word[9u]=(uint32_t)audio_ble_radio_identifier_triple_table_774bac[triple+1u]<<10u;
    word[10u]=(uint32_t)audio_ble_radio_identifier_triple_table_774bac[triple+2u]<<10u;
    word[12u]=*(volatile const uint32_t *)0xe00fefe0u&0xffu;
    audio_ble_hci_boot_delay_491102(10u);
    word[12u]|=(*(volatile const uint32_t *)0xe00fefe4u&15u)<<8u;
    audio_ble_hci_boot_delay_491102(10u);
    word[13u]=(*(volatile const uint32_t *)0xe00fefe4u&0xffu)>>4u;
    audio_ble_hci_boot_delay_491102(10u);
    word[13u]|=(*(volatile const uint32_t *)0xe00fefe8u&15u)<<4u;
    audio_ble_hci_boot_delay_491102(10u);
    word[14u]=*(volatile const uint32_t *)0xe00fefe8u&0xf0u;
    audio_ble_hci_boot_delay_491102(10u);
    word[14u]|=(*(volatile const uint32_t *)0xe00fefecu&0xffu)>>4u;
    audio_ble_hci_boot_delay_491102(10u);
    word[15u]=*(volatile const uint32_t *)0xe00feffcu<<24u;
    audio_ble_hci_boot_delay_491102(10u);
    word[15u]|=(*(volatile const uint32_t *)0xe00feff8u&0xffu)<<16u;
    audio_ble_hci_boot_delay_491102(10u);
    word[15u]|=(*(volatile const uint32_t *)0xe00feff4u&0xffu)<<8u;
    audio_ble_hci_boot_delay_491102(10u);
    word[15u]|=*(volatile const uint32_t *)0xe00feff0u&0xffu;
    audio_ble_hci_boot_delay_491102(10u);
}
