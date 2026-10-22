/* Product GATT services EFS / ESS / EUS / NUS / OTA: attribute tables and
 * groups (S6-fonts-residual storage-definition pass, G2 2.2.6.10).
 *
 * Stock owner: the first-party svc_* modules whose AddGroup / CbackRegister
 * helpers are ble/C2-even-services/svc_even_groups.c (0x5361bc..0x536233).
 * Layout follows the Cordio svc_*.c template: a static attsAttr_t list
 * (16 B each: pUuid, pValue, pLen, maxLen, settings, permissions) per
 * service, with the service / characteristic-declaration values, ROM
 * uint16_t lengths and 1-byte zero characteristic values all in ROM, the CCC
 * cells in .bss (0x20074f3c.., zero-initialised) and the attsGroup_t record
 * (20 B) in initialised .data. .data values come from the decoded 0x20000000
 * init stream (scatter record 0x75d3f4; pNext/readCback/writeCback are 0 and
 * are set at run time by AttsAddGroup / svc_*_cback_register); ROM bytes are
 * copied from ota_s200_firmware_ota.bin (VA = file offset + 0x437fe0).
 * attPrimSvcUuid / attChUuid / attCliChCfgUuid are Cordio att_uuid.c objects
 * (ROM 0x78f53c / 0x78f53e / 0x78f540) and are referenced, not defined.
 * Absolute placement is a linker obligation; compiling this file does not
 * establish byte identity. */
#include <stdint.h>

#define ATTS_SET_UUID_128     0x01u
#define ATTS_SET_WRITE_CBACK  0x02u
#define ATTS_SET_READ_CBACK   0x04u
#define ATTS_SET_VARIABLE_LEN 0x08u
#define ATTS_SET_ALLOW_OFFSET 0x10u
#define ATTS_SET_CCC          0x20u
#define ATTS_PERMIT_READ      0x01u
#define ATTS_PERMIT_WRITE     0x10u

/* Cordio attsAttr_t / attsGroup_t (att_api.h); pValue / pLen of the ROM
 * attributes point at const storage exactly as in stock. */
typedef struct {
    const uint8_t *pUuid;   /* +0x0 */
    const uint8_t *pValue;  /* +0x4 */
    const uint16_t *pLen;   /* +0x8 */
    uint16_t maxLen;        /* +0xc */
    uint8_t settings;       /* +0xe */
    uint8_t permissions;    /* +0xf */
} g2_atts_attr_t;
_Static_assert(sizeof(g2_atts_attr_t) == 16u, "Cordio attsAttr_t");

typedef struct {
    void *pNext;            /* +0x00 */
    const void *pAttr;      /* +0x04 */
    void *readCback;        /* +0x08 */
    void *writeCback;       /* +0x0c */
    uint16_t startHandle;   /* +0x10 */
    uint16_t endHandle;     /* +0x12 */
} g2_atts_group_t;
_Static_assert(sizeof(g2_atts_group_t) == 20u, "Cordio attsGroup_t");

extern const uint8_t attPrimSvcUuid[2];  /* Cordio att_uuid.c, ROM 0x78f53c, 0x2800 */
extern const uint8_t attChUuid[2];       /* Cordio att_uuid.c, ROM 0x78f53e, 0x2803 */
extern const uint8_t attCliChCfgUuid[2]; /* Cordio att_uuid.c, ROM 0x78f540, 0x2902 */

/* ---- EFS: group RAM 0x20003b24, attribute list ROM 0x6de974, handles 0x0880..0x0885 ---- */
static const uint8_t g2_svc_efs_uuid_7894a0[16] = {0x01, 0x74, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894a0 */
static const uint8_t g2_svc_efs_uuid_7894b0[16] = {0x02, 0x74, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894b0 */
static const uint8_t g2_svc_efs_val_svc_7894c0[16] = {0x50, 0x74, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894c0 */
static const uint8_t g2_svc_efs_val_ch_783ab4[19] = {0x04, 0x82, 0x08, 0x01, 0x74, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783ab4 */
static const uint8_t g2_svc_efs_val_78f6e9[1] = {0x00}; /* ROM 0x78f6e9 */
static const uint8_t g2_svc_efs_val_ch_783ac8[19] = {0x10, 0x84, 0x08, 0x02, 0x74, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783ac8 */
static const uint8_t g2_svc_efs_val_78f6ea[1] = {0x00}; /* ROM 0x78f6ea */
uint8_t g2_svc_efs_ccc_20074f3c[2] __attribute__((aligned(2))); /* RAM 0x20074f3c, .bss CCC value */
static const uint16_t g2_svc_efs_len_78f65e = 16u; /* ROM 0x78f65e */
static const uint16_t g2_svc_efs_len_78f660 = 19u; /* ROM 0x78f660 */
static const uint16_t g2_svc_efs_len_78f662 = 19u; /* ROM 0x78f662 */
static const uint16_t g2_svc_efs_len_78f664 = 1u; /* ROM 0x78f664 */
static const uint16_t g2_svc_efs_len_78f666 = 1u; /* ROM 0x78f666 */
static const uint16_t g2_svc_efs_len_78f668 = 2u; /* ROM 0x78f668 */
static const g2_atts_attr_t g2_svc_efs_attr_list_6de974[6] = { /* ROM 0x6de974 */
    {attPrimSvcUuid, g2_svc_efs_val_svc_7894c0, &g2_svc_efs_len_78f65e, 16u, 0u, ATTS_PERMIT_READ},
    {attChUuid, g2_svc_efs_val_ch_783ab4, &g2_svc_efs_len_78f660, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_efs_uuid_7894a0, g2_svc_efs_val_78f6e9, &g2_svc_efs_len_78f664, 512u, ATTS_SET_UUID_128 | ATTS_SET_WRITE_CBACK | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_WRITE},
    {attChUuid, g2_svc_efs_val_ch_783ac8, &g2_svc_efs_len_78f662, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_efs_uuid_7894b0, g2_svc_efs_val_78f6ea, &g2_svc_efs_len_78f666, 512u, ATTS_SET_UUID_128 | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ},
    {attCliChCfgUuid, g2_svc_efs_ccc_20074f3c, &g2_svc_efs_len_78f668, 2u, ATTS_SET_CCC, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
g2_atts_group_t svc_efs_group_20003b24 = { /* RAM 0x20003b24, .data */
    0, g2_svc_efs_attr_list_6de974, 0, 0, 0x0880u, 0x0885u
};

/* ---- ESS: group RAM 0x20003b38, attribute list ROM 0x6de9d4, handles 0x0860..0x0865 ---- */
static const uint8_t g2_svc_ess_uuid_7894d0[16] = {0x01, 0x64, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894d0 */
static const uint8_t g2_svc_ess_uuid_7894e0[16] = {0x02, 0x64, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894e0 */
static const uint8_t g2_svc_ess_val_svc_7894f0[16] = {0x50, 0x64, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x7894f0 */
static const uint8_t g2_svc_ess_val_ch_783adc[19] = {0x04, 0x62, 0x08, 0x01, 0x64, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783adc */
static const uint8_t g2_svc_ess_val_78f6eb[1] = {0x00}; /* ROM 0x78f6eb */
static const uint8_t g2_svc_ess_val_ch_783af0[19] = {0x10, 0x64, 0x08, 0x02, 0x64, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783af0 */
static const uint8_t g2_svc_ess_val_78f6ec[1] = {0x00}; /* ROM 0x78f6ec */
uint8_t g2_svc_ess_ccc_20074f3e[2] __attribute__((aligned(2))); /* RAM 0x20074f3e, .bss CCC value */
static const uint16_t g2_svc_ess_len_78f66a = 16u; /* ROM 0x78f66a */
static const uint16_t g2_svc_ess_len_78f66c = 19u; /* ROM 0x78f66c */
static const uint16_t g2_svc_ess_len_78f66e = 19u; /* ROM 0x78f66e */
static const uint16_t g2_svc_ess_len_78f670 = 1u; /* ROM 0x78f670 */
static const uint16_t g2_svc_ess_len_78f672 = 1u; /* ROM 0x78f672 */
static const uint16_t g2_svc_ess_len_78f674 = 2u; /* ROM 0x78f674 */
static const g2_atts_attr_t g2_svc_ess_attr_list_6de9d4[6] = { /* ROM 0x6de9d4 */
    {attPrimSvcUuid, g2_svc_ess_val_svc_7894f0, &g2_svc_ess_len_78f66a, 16u, 0u, ATTS_PERMIT_READ},
    {attChUuid, g2_svc_ess_val_ch_783adc, &g2_svc_ess_len_78f66c, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_ess_uuid_7894d0, g2_svc_ess_val_78f6eb, &g2_svc_ess_len_78f670, 512u, ATTS_SET_UUID_128 | ATTS_SET_WRITE_CBACK | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_WRITE},
    {attChUuid, g2_svc_ess_val_ch_783af0, &g2_svc_ess_len_78f66e, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_ess_uuid_7894e0, g2_svc_ess_val_78f6ec, &g2_svc_ess_len_78f672, 512u, ATTS_SET_UUID_128 | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ},
    {attCliChCfgUuid, g2_svc_ess_ccc_20074f3e, &g2_svc_ess_len_78f674, 2u, ATTS_SET_CCC, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
g2_atts_group_t svc_ess_group_20003b38 = { /* RAM 0x20003b38, .data */
    0, g2_svc_ess_attr_list_6de9d4, 0, 0, 0x0860u, 0x0865u
};

/* ---- EUS: group RAM 0x20003b4c, attribute list ROM 0x6dea34, handles 0x0840..0x0845 ---- */
static const uint8_t g2_svc_eus_uuid_789500[16] = {0x01, 0x54, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789500 */
static const uint8_t g2_svc_eus_uuid_789510[16] = {0x02, 0x54, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789510 */
static const uint8_t g2_svc_eus_val_svc_789520[16] = {0x50, 0x54, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789520 */
static const uint8_t g2_svc_eus_val_ch_783b04[19] = {0x04, 0x42, 0x08, 0x01, 0x54, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783b04 */
static const uint8_t g2_svc_eus_val_78f6ed[1] = {0x00}; /* ROM 0x78f6ed */
static const uint8_t g2_svc_eus_val_ch_783b18[19] = {0x10, 0x44, 0x08, 0x02, 0x54, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783b18 */
static const uint8_t g2_svc_eus_val_78f6ee[1] = {0x00}; /* ROM 0x78f6ee */
uint8_t g2_svc_eus_ccc_20074f40[2] __attribute__((aligned(2))); /* RAM 0x20074f40, .bss CCC value */
static const uint16_t g2_svc_eus_len_78f676 = 16u; /* ROM 0x78f676 */
static const uint16_t g2_svc_eus_len_78f678 = 19u; /* ROM 0x78f678 */
static const uint16_t g2_svc_eus_len_78f67a = 19u; /* ROM 0x78f67a */
static const uint16_t g2_svc_eus_len_78f67c = 1u; /* ROM 0x78f67c */
static const uint16_t g2_svc_eus_len_78f67e = 1u; /* ROM 0x78f67e */
static const uint16_t g2_svc_eus_len_78f680 = 2u; /* ROM 0x78f680 */
static const g2_atts_attr_t g2_svc_eus_attr_list_6dea34[6] = { /* ROM 0x6dea34 */
    {attPrimSvcUuid, g2_svc_eus_val_svc_789520, &g2_svc_eus_len_78f676, 16u, 0u, ATTS_PERMIT_READ},
    {attChUuid, g2_svc_eus_val_ch_783b04, &g2_svc_eus_len_78f678, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_eus_uuid_789500, g2_svc_eus_val_78f6ed, &g2_svc_eus_len_78f67c, 512u, ATTS_SET_UUID_128 | ATTS_SET_WRITE_CBACK | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_WRITE},
    {attChUuid, g2_svc_eus_val_ch_783b18, &g2_svc_eus_len_78f67a, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_eus_uuid_789510, g2_svc_eus_val_78f6ee, &g2_svc_eus_len_78f67e, 512u, ATTS_SET_UUID_128 | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ},
    {attCliChCfgUuid, g2_svc_eus_ccc_20074f40, &g2_svc_eus_len_78f680, 2u, ATTS_SET_CCC, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
g2_atts_group_t svc_eus_group_20003b4c = { /* RAM 0x20003b4c, .data */
    0, g2_svc_eus_attr_list_6dea34, 0, 0, 0x0840u, 0x0845u
};

/* ---- NUS: group RAM 0x20003ba4, attribute list ROM 0x6dea94, handles 0x08a0..0x08a5 ---- */
static const uint8_t g2_svc_nus_uuid_789530[16] = {0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0, 0x93, 0xf3, 0xa3, 0xb5, 0x02, 0x00, 0x40, 0x6e}; /* ROM 0x789530 */
static const uint8_t g2_svc_nus_uuid_789540[16] = {0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0, 0x93, 0xf3, 0xa3, 0xb5, 0x03, 0x00, 0x40, 0x6e}; /* ROM 0x789540 */
static const uint8_t g2_svc_nus_val_svc_789550[16] = {0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0, 0x93, 0xf3, 0xa3, 0xb5, 0x01, 0x00, 0x40, 0x6e}; /* ROM 0x789550 */
static const uint8_t g2_svc_nus_val_ch_783b2c[19] = {0x0c, 0xa2, 0x08, 0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0, 0x93, 0xf3, 0xa3, 0xb5, 0x02, 0x00, 0x40, 0x6e}; /* ROM 0x783b2c */
static const uint8_t g2_svc_nus_val_78f6ef[1] = {0x00}; /* ROM 0x78f6ef */
static const uint8_t g2_svc_nus_val_ch_783b40[19] = {0x10, 0xa4, 0x08, 0x9e, 0xca, 0xdc, 0x24, 0x0e, 0xe5, 0xa9, 0xe0, 0x93, 0xf3, 0xa3, 0xb5, 0x03, 0x00, 0x40, 0x6e}; /* ROM 0x783b40 */
static const uint8_t g2_svc_nus_val_78f6f0[1] = {0x00}; /* ROM 0x78f6f0 */
uint8_t g2_svc_nus_ccc_20074f44[2] __attribute__((aligned(2))); /* RAM 0x20074f44, .bss CCC value */
static const uint16_t g2_svc_nus_len_78f6a6 = 16u; /* ROM 0x78f6a6 */
static const uint16_t g2_svc_nus_len_78f6a8 = 19u; /* ROM 0x78f6a8 */
static const uint16_t g2_svc_nus_len_78f6aa = 19u; /* ROM 0x78f6aa */
static const uint16_t g2_svc_nus_len_78f6ac = 1u; /* ROM 0x78f6ac */
static const uint16_t g2_svc_nus_len_78f6ae = 1u; /* ROM 0x78f6ae */
static const uint16_t g2_svc_nus_len_78f6b0 = 2u; /* ROM 0x78f6b0 */
static const g2_atts_attr_t g2_svc_nus_attr_list_6dea94[6] = { /* ROM 0x6dea94 */
    {attPrimSvcUuid, g2_svc_nus_val_svc_789550, &g2_svc_nus_len_78f6a6, 16u, 0u, ATTS_PERMIT_READ},
    {attChUuid, g2_svc_nus_val_ch_783b2c, &g2_svc_nus_len_78f6a8, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_nus_uuid_789530, g2_svc_nus_val_78f6ef, &g2_svc_nus_len_78f6ac, 512u, ATTS_SET_UUID_128 | ATTS_SET_WRITE_CBACK | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_WRITE},
    {attChUuid, g2_svc_nus_val_ch_783b40, &g2_svc_nus_len_78f6aa, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_nus_uuid_789540, g2_svc_nus_val_78f6f0, &g2_svc_nus_len_78f6ae, 512u, ATTS_SET_UUID_128 | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ},
    {attCliChCfgUuid, g2_svc_nus_ccc_20074f44, &g2_svc_nus_len_78f6b0, 2u, ATTS_SET_CCC, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
g2_atts_group_t svc_nus_group_20003ba4 = { /* RAM 0x20003ba4, .data */
    0, g2_svc_nus_attr_list_6dea94, 0, 0, 0x08a0u, 0x08a5u
};

/* ---- OTA: group RAM 0x20003bb8, attribute list ROM 0x6deaf4, handles 0x0820..0x0825 ---- */
static const uint8_t g2_svc_ota_uuid_789560[16] = {0x01, 0x00, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789560 */
static const uint8_t g2_svc_ota_uuid_789570[16] = {0x02, 0x00, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789570 */
static const uint8_t g2_svc_ota_val_svc_789580[16] = {0x01, 0x10, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x789580 */
static const uint8_t g2_svc_ota_val_ch_783b54[19] = {0x04, 0x22, 0x08, 0x01, 0x00, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783b54 */
static const uint8_t g2_svc_ota_val_78f6f1[1] = {0x00}; /* ROM 0x78f6f1 */
static const uint8_t g2_svc_ota_val_ch_783b68[19] = {0x10, 0x24, 0x08, 0x02, 0x00, 0x2e, 0xc7, 0x8a, 0x0e, 0x73, 0x90, 0xe1, 0x11, 0xc2, 0x08, 0x60, 0x27, 0x00, 0x00}; /* ROM 0x783b68 */
static const uint8_t g2_svc_ota_val_78f6f2[1] = {0x00}; /* ROM 0x78f6f2 */
uint8_t g2_svc_ota_ccc_20074f46[2] __attribute__((aligned(2))); /* RAM 0x20074f46, .bss CCC value */
static const uint16_t g2_svc_ota_len_78f6b2 = 16u; /* ROM 0x78f6b2 */
static const uint16_t g2_svc_ota_len_78f6b4 = 19u; /* ROM 0x78f6b4 */
static const uint16_t g2_svc_ota_len_78f6b6 = 19u; /* ROM 0x78f6b6 */
static const uint16_t g2_svc_ota_len_78f6b8 = 1u; /* ROM 0x78f6b8 */
static const uint16_t g2_svc_ota_len_78f6ba = 1u; /* ROM 0x78f6ba */
static const uint16_t g2_svc_ota_len_78f6bc = 2u; /* ROM 0x78f6bc */
static const g2_atts_attr_t g2_svc_ota_attr_list_6deaf4[6] = { /* ROM 0x6deaf4 */
    {attPrimSvcUuid, g2_svc_ota_val_svc_789580, &g2_svc_ota_len_78f6b2, 16u, 0u, ATTS_PERMIT_READ},
    {attChUuid, g2_svc_ota_val_ch_783b54, &g2_svc_ota_len_78f6b4, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_ota_uuid_789560, g2_svc_ota_val_78f6f1, &g2_svc_ota_len_78f6b8, 512u, ATTS_SET_UUID_128 | ATTS_SET_WRITE_CBACK | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_WRITE},
    {attChUuid, g2_svc_ota_val_ch_783b68, &g2_svc_ota_len_78f6b6, 19u, 0u, ATTS_PERMIT_READ},
    {g2_svc_ota_uuid_789570, g2_svc_ota_val_78f6f2, &g2_svc_ota_len_78f6ba, 512u, ATTS_SET_UUID_128 | ATTS_SET_VARIABLE_LEN, ATTS_PERMIT_READ},
    {attCliChCfgUuid, g2_svc_ota_ccc_20074f46, &g2_svc_ota_len_78f6bc, 2u, ATTS_SET_CCC, ATTS_PERMIT_READ | ATTS_PERMIT_WRITE},
};
g2_atts_group_t svc_ota_group_20003bb8 = { /* RAM 0x20003bb8, .data */
    0, g2_svc_ota_attr_list_6deaf4, 0, 0, 0x0820u, 0x0825u
};
