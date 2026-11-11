/* SPDX-License-Identifier: MIT
 * Source reconstruction candidate for the EM9305 NVM bootloader.
 * The authenticated record 0/1 disassembly and the SDK 4.6 public prototypes
 * define this interface. This candidate has not been tested on G2 hardware.
 */
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define NVM_START UINT32_C(0x00300000)
#define NVM_END UINT32_C(0x00380000)
#define NVM_PAGE_SIZE UINT32_C(0x2000)
#define HEADER_MAGIC UINT32_C(0x52444846)
#define HEADER_NOT_FOUND UINT32_MAX
#define HEADER_COUNT 10u
#ifdef G2_EM_BOOT_HOST_TEST
#define BOOT_TEXT
#define BOOT_ENTRY
#else
#define BOOT_TEXT __attribute__((section(".nvm_bootloader.text")))
#define BOOT_ENTRY __attribute__((section(".nvm_bootloader.entry"), used))
#endif

struct __attribute__((packed)) nvm_header {
    uint32_t magic;
    uint8_t version;
    uint8_t size;
    uint8_t section;
    uint8_t reserved;
    uint32_t firmware_start;
    uint32_t firmware_size;
    uint32_t firmware_crc;
    uint32_t emcore_crc;
    uint32_t options;
    uint16_t firmware_version;
    uint32_t execution;
    uint32_t header_crc;
    uint16_t padding;
};

_Static_assert(sizeof(struct nvm_header) == 40, "NVM header layout");
_Static_assert(offsetof(struct nvm_header, header_crc) == 34, "NVM header CRC offset");

#ifdef G2_EM_BOOT_HOST_TEST
extern volatile uint8_t *g2_em_boot_test_flash;
extern volatile uint32_t g2_em_boot_test_pml_status;
extern volatile uint8_t g2_em_boot_test_crc_state;
extern volatile uint16_t g2_em_boot_test_reset_flags;
#define NVM_POINTER(address) (g2_em_boot_test_flash + ((address) - NVM_START))
#define PML_STATUS g2_em_boot_test_pml_status
#define PML_CRC_STATE g2_em_boot_test_crc_state
#define RESET_FLAGS g2_em_boot_test_reset_flags
#else
#define NVM_POINTER(address) ((volatile uint8_t *)(uintptr_t)(address))
#define PML_STATUS (*(volatile uint32_t *)(uintptr_t)0x00f00430)
#define PML_CRC_STATE (*(volatile uint8_t *)(uintptr_t)0x00f00408)
#define RESET_FLAGS (*(volatile uint16_t *)(uintptr_t)0x0080fe22)
#endif

#define PML_BOOT_MODE_MASK (UINT32_C(3) << 16)
#define PML_EMCORE_MODE (UINT32_C(1) << 16)
#define PML_BOOTLOADER_MODE (UINT32_C(2) << 16)
#define PML_CRC_FLAG (UINT32_C(1) << 18)

static BOOT_TEXT const volatile struct nvm_header *header_at(uint32_t address)
{
    return (const volatile struct nvm_header *)NVM_POINTER(address);
}

static BOOT_TEXT uint32_t crc32_nvm(uint32_t address, uint32_t count)
{
    uint32_t crc = UINT32_MAX;
    const volatile uint8_t *bytes = NVM_POINTER(address);
    for (uint32_t i = 0; i < count; ++i) {
        crc ^= bytes[i];
        for (unsigned bit = 0; bit < 8; ++bit) {
            crc = (crc >> 1) ^ ((crc & 1u) ? UINT32_C(0xedb88320) : 0u);
        }
    }
    return ~crc;
}

BOOT_TEXT uint8_t nvmbl_getEmHdr_SupportedVersion(void) { return 0; }
BOOT_TEXT uint8_t nvmbl_getEmHdr_HdrVersionSize(uint32_t address) { return header_at(address)->size; }
BOOT_TEXT uint8_t nvmbl_getEmHdr_HdrVersion(uint32_t address) { return header_at(address)->version; }
BOOT_TEXT uint8_t nvmbl_getEmHdr_SectionCode(uint32_t address) { return header_at(address)->section; }
BOOT_TEXT uint16_t nvmbl_getEmHdr_FirmwareVersion(uint32_t address) { return header_at(address)->firmware_version; }
BOOT_TEXT uint32_t nvmbl_getEmHdr_ExeAddress(uint32_t address) { return header_at(address)->execution; }
BOOT_TEXT uint32_t nvmbl_getEmHdr_EMCoreCRC(uint32_t address) { return header_at(address)->emcore_crc; }
BOOT_TEXT uint32_t nvmbl_getEmHdr_FirmwareSize(uint32_t address) { return header_at(address)->firmware_size; }
BOOT_TEXT uint32_t nvmbl_getEmHdr_FirmwareOptions(uint32_t address) { return header_at(address)->options; }

BOOT_TEXT uint32_t nvmbl_getEmHdr_FindHdr(uint32_t start)
{
    if (start < NVM_START || start >= NVM_END) return HEADER_NOT_FOUND;
    uint32_t page = start & ~(NVM_PAGE_SIZE - 1u);
    for (; page <= NVM_END - NVM_PAGE_SIZE; page += NVM_PAGE_SIZE) {
        const volatile struct nvm_header *header = header_at(page);
        if (header->magic != HEADER_MAGIC) continue;
        if (crc32_nvm(page, offsetof(struct nvm_header, header_crc)) == header->header_crc)
            return page;
    }
    return HEADER_NOT_FOUND;
}

BOOT_TEXT uint32_t nvmbl_getEmHdr_VerifyFirmwarePayload(uint32_t address)
{
    const volatile struct nvm_header *header = header_at(address);
    uint32_t start = header->firmware_start;
    uint32_t size = header->firmware_size;
    if (start < NVM_START || start >= NVM_END || size > NVM_END - start) return 1;
    return crc32_nvm(start, size) != header->firmware_crc;
}

BOOT_TEXT void initHeaderEntryValues(uint32_t entries[HEADER_COUNT])
{
    for (unsigned i = 0; i < HEADER_COUNT; ++i) entries[i] = HEADER_NOT_FOUND;
}

BOOT_TEXT void saveHeaderEntry(uint32_t entries[HEADER_COUNT], uint32_t address)
{
    if (address == HEADER_NOT_FOUND) return;
    uint8_t section = nvmbl_getEmHdr_SectionCode(address);
    if (section < HEADER_COUNT) entries[section] = address;
}

BOOT_TEXT uint32_t getNextPageIfHeaderAddress(uint32_t address)
{
    if (address == HEADER_NOT_FOUND) return HEADER_NOT_FOUND;
    return nvmbl_getEmHdr_SectionCode(address) < HEADER_COUNT
        ? address + NVM_PAGE_SIZE : address;
}

BOOT_TEXT void getAllHeaderEntries(uint32_t entries[HEADER_COUNT])
{
    initHeaderEntryValues(entries);
    uint32_t search = NVM_START;
    for (unsigned found = 0; found < HEADER_COUNT && search != HEADER_NOT_FOUND; ++found) {
        uint32_t header = nvmbl_getEmHdr_FindHdr(search);
        if (header == HEADER_NOT_FOUND) break;
        saveHeaderEntry(entries, header);
        search = getNextPageIfHeaderAddress(header);
    }
}

BOOT_TEXT bool runChecksum(uint16_t reset_flags)
{
    return (reset_flags & 0x300u) == 0u || PML_CRC_STATE == 0u;
}

BOOT_TEXT void checkCRCHeader(uint32_t *entry)
{
    if (*entry != HEADER_NOT_FOUND &&
        (nvmbl_getEmHdr_FirmwareOptions(*entry) & 0x100u) == 0 &&
        nvmbl_getEmHdr_VerifyFirmwarePayload(*entry) != 0)
        *entry = HEADER_NOT_FOUND;
}

BOOT_TEXT void checkCRC(uint32_t entries[HEADER_COUNT], uint16_t reset_flags)
{
    if (!runChecksum(reset_flags)) return;
    PML_STATUS &= ~PML_CRC_FLAG;
    for (unsigned i = 0; i < HEADER_COUNT; ++i) checkCRCHeader(&entries[i]);
}

BOOT_TEXT void loadBootLoaderFunction(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    if (*entry != 0 || (PML_STATUS & PML_BOOT_MODE_MASK) != PML_BOOTLOADER_MODE)
        return;
    uint32_t header = entries[0] != HEADER_NOT_FOUND ? entries[0] : entries[4];
    if (header != HEADER_NOT_FOUND) *entry = nvmbl_getEmHdr_ExeAddress(header);
}

BOOT_TEXT void loadEmCoreFunction(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    if (*entry == 0 && (PML_STATUS & PML_BOOT_MODE_MASK) == PML_EMCORE_MODE &&
        entries[1] != HEADER_NOT_FOUND)
        *entry = nvmbl_getEmHdr_ExeAddress(entries[1]);
}

BOOT_TEXT void loadCustomerApplication(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    if (*entry != 0 || entries[3] == HEADER_NOT_FOUND) return;
    *entry = nvmbl_getEmHdr_ExeAddress(entries[3]);
    uint32_t mode = PML_STATUS & PML_BOOT_MODE_MASK;
    if (mode == PML_BOOTLOADER_MODE || mode == PML_EMCORE_MODE) {
        PML_STATUS &= ~PML_BOOT_MODE_MASK;
        PML_STATUS |= PML_CRC_FLAG;
    }
}

BOOT_TEXT void loadCustomerBootLoader(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    if (*entry != 0) return;
    uint32_t header = entries[0] != HEADER_NOT_FOUND ? entries[0] : entries[4];
    if (header == HEADER_NOT_FOUND) return;
    *entry = nvmbl_getEmHdr_ExeAddress(header);
    PML_STATUS &= ~PML_BOOT_MODE_MASK;
    PML_STATUS |= PML_BOOTLOADER_MODE;
    PML_STATUS |= PML_CRC_FLAG;
}

BOOT_TEXT void loadEmCoreApplication(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    if (*entry != 0 || entries[1] == HEADER_NOT_FOUND) return;
    *entry = nvmbl_getEmHdr_ExeAddress(entries[1]);
    PML_STATUS &= ~PML_BOOT_MODE_MASK;
    PML_STATUS |= PML_EMCORE_MODE;
    PML_STATUS |= PML_CRC_FLAG;
}

BOOT_TEXT void getMainFunction(uint32_t entries[HEADER_COUNT], uint32_t *entry)
{
    loadBootLoaderFunction(entries, entry);
    loadEmCoreFunction(entries, entry);
    loadCustomerApplication(entries, entry);
    loadCustomerBootLoader(entries, entry);
    loadEmCoreApplication(entries, entry);
}

BOOT_TEXT void jumpToFunction(uint32_t entry)
{
    if (entry != 0) ((void (*)(void))(uintptr_t)entry)();
}

static BOOT_TEXT void PML_SetCRCErrorFlag(void)
{
    PML_STATUS |= PML_CRC_FLAG;
}

BOOT_ENTRY void nvm_bootloader(void)
{
    uint32_t entries[HEADER_COUNT];
    getAllHeaderEntries(entries);
    checkCRC(entries, RESET_FLAGS);
    uint32_t entry = 0;
    getMainFunction(entries, &entry);
    jumpToFunction(entry);
    /* Stock marks CRC failure, requests reset, and enters its ROM reset
     * routine if the selected NVM entry returns or no image was selected. */
    PML_SetCRCErrorFlag();
    PML_STATUS |= UINT32_C(1) << 23;
    ((void (*)(void))(uintptr_t)0x00103f14)();
    for (;;) { __asm__ volatile ("nop"); }
}
