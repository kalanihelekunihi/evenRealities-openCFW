/* Source-built first flash page for R1. The bootloader update command
 * stages a record at 0xFE000; only this page executes while 0xF8000 is
 * erased and copied. A torn copy is replayed after reset from its original
 * staging source. The bootloader must validate and authenticate that source
 * before it writes the record. */
#include <stdint.h>
#include "nrf.h"
#include "nrf_error.h"
#include "nrf_mbr.h"
#include "copy_record.h"
#include "../shared/cordio_region_descriptor.h"
#include <stddef.h>

#define R1_NVMC_READY (*(volatile uint32_t *)0x4001e400u)
#define R1_NVMC_CONFIG (*(volatile uint32_t *)0x4001e504u)
#define R1_NVMC_ERASEPAGE (*(volatile uint32_t *)0x4001e508u)
#define R1_FICR_PAGE_SIZE (*(volatile const uint32_t *)0x10000010u)
#define R1_FICR_PAGE_COUNT (*(volatile const uint32_t *)0x10000014u)
#define R1_UICR_BOOTLOADER (*(volatile const uint32_t *)0x10001014u)
#define R1_SCB_VTOR (*(volatile uint32_t *)0xe000ed08u)

static int ready(void)
{
    uint32_t remaining = 10000000u;
    while (R1_NVMC_READY == 0u && remaining != 0u) {
        --remaining;
    }
    return remaining != 0u;
}

static int erase_page(uint32_t address)
{
    if (!ready()) return 0;
    R1_NVMC_CONFIG = 2u;
    if (!ready()) {
        R1_NVMC_CONFIG = 0u;
        return 0;
    }
    R1_NVMC_ERASEPAGE = address;
    if (!ready()) {
        R1_NVMC_CONFIG = 0u;
        return 0;
    }
    R1_NVMC_CONFIG = 0u;
    return ready();
}

static int write_word(uint32_t address, uint32_t value)
{
    if (!ready()) return 0;
    R1_NVMC_CONFIG = 1u;
    if (!ready()) {
        R1_NVMC_CONFIG = 0u;
        return 0;
    }
    *(volatile uint32_t *)address = value;
    if (!ready()) {
        R1_NVMC_CONFIG = 0u;
        return 0;
    }
    R1_NVMC_CONFIG = 0u;
    return ready() && *(volatile const uint32_t *)address == value;
}

static int record_valid(const r1_mbr_copy_record_t *record)
{
    uint32_t source = record->source;
    uint32_t length = record->length_words;
    return record->magic == R1_MBR_COPY_MAGIC &&
           record->magic_inverse == ~R1_MBR_COPY_MAGIC &&
           record->destination == R1_MBR_BOOTLOADER_BASE &&
           record->checksum == r1_mbr_copy_checksum(source, length,
                                                     record->destination) &&
           (source & 3u) == 0u &&
           source >= R1_MBR_APPLICATION_BASE &&
           source < R1_MBR_BOOTLOADER_BASE &&
           length != 0u &&
           length <= (R1_MBR_BOOTLOADER_LIMIT - R1_MBR_BOOTLOADER_BASE) / 4u &&
           length <= (R1_MBR_BOOTLOADER_BASE - source) / 4u;
}

static int copy_bootloader(const r1_mbr_copy_record_t *record)
{
    uint32_t words = record->length_words;
    uint32_t source = record->source;
    uint32_t page_count = (words + (R1_MBR_PAGE_BYTES / 4u - 1u)) /
                          (R1_MBR_PAGE_BYTES / 4u);
    for (uint32_t page = 0; page < page_count; ++page) {
        uint32_t destination = R1_MBR_BOOTLOADER_BASE + page * R1_MBR_PAGE_BYTES;
        if (!erase_page(destination)) return 0;
        for (uint32_t word = 0; word < R1_MBR_PAGE_BYTES / 4u; ++word) {
            uint32_t index = page * (R1_MBR_PAGE_BYTES / 4u) + word;
            if (index == words) break;
            uint32_t value = *(volatile const uint32_t *)(source + index * 4u);
            if (!write_word(destination + word * 4u, value)) return 0;
        }
    }
    /* Do not invalidate the replay record until the whole image verifies. */
    for (uint32_t word = 0; word < words; ++word) {
        if (*(volatile const uint32_t *)(source + word * 4u) !=
            *(volatile const uint32_t *)(R1_MBR_BOOTLOADER_BASE + word * 4u))
            return 0;
    }
    return write_word(R1_MBR_COPY_PAGE, 0u) && erase_page(R1_MBR_COPY_PAGE);
}

/* This source-built first-page ABI is checked before the bootloader calls
 * it. It executes independently of the bootloader while staging its replay
 * record, and the reset path above performs the actual copy. */
const uint32_t r1_mbr_stage_tag
    __attribute__((section(".mbr_stage_tag"), used)) = R1_MBR_STAGE_TAG;

uint32_t r1_mbr_stage_bootloader(uint32_t source, uint32_t words)
    __attribute__((section(".mbr_stage_entry"), used));

uint32_t r1_mbr_stage_bootloader(uint32_t source, uint32_t words)
{
    if (R1_FICR_PAGE_SIZE != R1_MBR_PAGE_BYTES ||
        R1_FICR_PAGE_COUNT != 256u)
        return R1_MBR_STAGE_UNSUPPORTED;
    if (R1_UICR_BOOTLOADER != R1_MBR_BOOTLOADER_BASE)
        return R1_MBR_STAGE_FORBIDDEN;
    if (words == 0u ||
        words > (R1_MBR_BOOTLOADER_LIMIT - R1_MBR_BOOTLOADER_BASE) / 4u)
        return R1_MBR_STAGE_LENGTH;
    if ((source & 3u) != 0u || source < R1_MBR_APPLICATION_BASE ||
        source >= R1_MBR_BOOTLOADER_BASE ||
        words > (R1_MBR_BOOTLOADER_BASE - source) / 4u)
        return R1_MBR_STAGE_ADDRESS;
    if (!erase_page(R1_MBR_COPY_PAGE) ||
        *(volatile const uint32_t *)R1_MBR_COPY_PAGE != 0xffffffffu)
        return R1_MBR_STAGE_FLASH_ERROR;
    uint32_t checksum = r1_mbr_copy_checksum(source, words,
                                              R1_MBR_BOOTLOADER_BASE);
    if (!write_word(R1_MBR_COPY_PAGE + 8u, source) ||
        !write_word(R1_MBR_COPY_PAGE + 12u, words) ||
        !write_word(R1_MBR_COPY_PAGE + 16u, R1_MBR_BOOTLOADER_BASE) ||
        !write_word(R1_MBR_COPY_PAGE + 20u, checksum) ||
        !write_word(R1_MBR_COPY_PAGE + 4u, ~R1_MBR_COPY_MAGIC) ||
        !write_word(R1_MBR_COPY_PAGE, R1_MBR_COPY_MAGIC))
        return R1_MBR_STAGE_FLASH_ERROR;
    __DSB();
    NVIC_SystemReset();
    for (;;) { }
}

/* First-page Cordio RAM initializer. It remains available while the upper
 * application is absent and validates every callable lower-flash entry
 * before touching RAM. The bootloader calls it only after checking the tag. */
const uint32_t r1_mbr_cordio_init_tag
    __attribute__((section(".mbr_cordio_init_tag"), used)) =
        R1_MBR_CORDIO_INIT_TAG;

uint32_t r1_mbr_cordio_region_init(void)
    __attribute__((section(".mbr_cordio_init"), used));

uint32_t r1_mbr_cordio_region_init(void)
{
    const volatile r1_cordio_region_descriptor_t *desc =
        (const volatile r1_cordio_region_descriptor_t *)R1_CORDIO_FLASH_BASE;
    if (desc->magic != R1_CORDIO_DESCRIPTOR_MAGIC ||
        desc->version != R1_CORDIO_DESCRIPTOR_VERSION ||
        desc->bytes != sizeof(*desc) ||
        desc->flash_base != R1_CORDIO_FLASH_BASE ||
        desc->flash_limit != R1_CORDIO_FLASH_LIMIT ||
        desc->ram_base != R1_CORDIO_RAM_BASE ||
        desc->ram_limit != R1_CORDIO_RAM_LIMIT ||
        desc->bss_begin < R1_CORDIO_RAM_BASE ||
        desc->bss_begin >= desc->bss_end ||
        desc->bss_end > desc->data_begin ||
        desc->data_begin >= desc->data_end ||
        desc->data_end > R1_CORDIO_RAM_LIMIT ||
        desc->code_end <= R1_CORDIO_FLASH_BASE + sizeof(*desc) ||
        desc->code_end > desc->data_load ||
        desc->data_load >= R1_CORDIO_FLASH_LIMIT ||
        desc->data_end - desc->data_begin >
            R1_CORDIO_FLASH_LIMIT - desc->data_load ||
        __get_MSP() < R1_CORDIO_RAM_LIMIT)
        return 0u;
    const volatile uint32_t *entry = &desc->controller_bootstrap;
    const uint32_t count =
        (sizeof(*desc) -
         offsetof(r1_cordio_region_descriptor_t, controller_bootstrap)) /
        sizeof(uint32_t);
    for (uint32_t i = 0u; i < count; ++i) {
        uint32_t target = entry[i];
        if ((target & 1u) == 0u ||
            (target & ~1u) < R1_CORDIO_FLASH_BASE + sizeof(*desc) ||
            (target & ~1u) >= desc->code_end)
            return 0u;
    }
    for (uint32_t address = R1_CORDIO_RAM_BASE;
         address < R1_CORDIO_RAM_LIMIT; ++address)
        *(volatile uint8_t *)address = 0u;
    uint32_t source = desc->data_load;
    for (uint32_t destination = desc->data_begin;
         destination < desc->data_end; ++destination)
        *(volatile uint8_t *)destination =
            *(volatile const uint8_t *)source++;
    return 1u;
}

const uint32_t r1_mbr_command_tag
    __attribute__((section(".mbr_command_tag"), used)) =
        R1_MBR_COMMAND_TAG;

uint32_t r1_mbr_command_non_init(sd_mbr_command_t *command)
    __attribute__((section(".mbr_command"), used));

uint32_t r1_mbr_command_non_init(sd_mbr_command_t *command)
{
    if (command == 0) return NRF_ERROR_NULL;
    switch (command->command) {
    case SD_MBR_COMMAND_COPY_BL: {
        const sd_mbr_command_copy_bl_t *copy = &command->params.copy_bl;
        uint32_t result = r1_mbr_stage_bootloader(
            (uint32_t)(uintptr_t)copy->bl_src, copy->bl_len);
        switch (result) {
        case R1_MBR_STAGE_UNSUPPORTED: return NRF_ERROR_NOT_SUPPORTED;
        case R1_MBR_STAGE_FORBIDDEN: return NRF_ERROR_FORBIDDEN;
        case R1_MBR_STAGE_LENGTH: return NRF_ERROR_INVALID_LENGTH;
        case R1_MBR_STAGE_ADDRESS: return NRF_ERROR_INVALID_ADDR;
        case R1_MBR_STAGE_FLASH_ERROR: return NRF_ERROR_INTERNAL;
        default: return NRF_ERROR_INTERNAL;
        }
    }
    case SD_MBR_COMMAND_COMPARE: {
        const sd_mbr_command_compare_t *compare = &command->params.compare;
        if (compare->ptr1 == 0 || compare->ptr2 == 0)
            return NRF_ERROR_NULL;
        for (uint32_t i = 0u; i < compare->len; ++i)
            if (compare->ptr1[i] != compare->ptr2[i])
                return NRF_ERROR_NULL;
        return NRF_SUCCESS;
    }
    case SD_MBR_COMMAND_IRQ_FORWARD_ADDRESS_SET: {
        uint32_t base = command->params.irq_forward_address_set.address;
        if ((base & 0x1ffu) != 0u || base < R1_MBR_APPLICATION_BASE ||
            base >= R1_MBR_BOOTLOADER_LIMIT)
            return NRF_ERROR_INVALID_ADDR;
        R1_SCB_VTOR = base;
        __DSB();
        __ISB();
        return NRF_SUCCESS;
    }
    default:
        return NRF_ERROR_NOT_SUPPORTED;
    }
}

__attribute__((noreturn)) static void enter_bootloader(void)
{
    uint32_t stack = *(volatile const uint32_t *)R1_MBR_BOOTLOADER_BASE;
    uint32_t reset = *(volatile const uint32_t *)(R1_MBR_BOOTLOADER_BASE + 4u);
    if ((stack & 7u) != 0u || stack < 0x20000000u || stack > 0x20040000u ||
        (reset & 1u) == 0u || (reset & ~1u) < R1_MBR_BOOTLOADER_BASE ||
        (reset & ~1u) >= R1_MBR_BOOTLOADER_LIMIT) {
        for (;;) { }
    }
    R1_SCB_VTOR = R1_MBR_BOOTLOADER_BASE;
    __DSB();
    __ISB();
    __set_MSP(stack);
    ((void (*)(void))reset)();
    for (;;) { }
}

__attribute__((noreturn)) void Reset_Handler(void)
{
    if (R1_FICR_PAGE_SIZE != R1_MBR_PAGE_BYTES || R1_FICR_PAGE_COUNT != 256u)
        for (;;) { }
    const r1_mbr_copy_record_t *record =
        (const r1_mbr_copy_record_t *)R1_MBR_COPY_PAGE;
    if (record->magic == R1_MBR_COPY_MAGIC) {
        if (!record_valid(record) || !copy_bootloader(record))
            for (;;) { }
    }
    enter_bootloader();
}

__attribute__((noreturn)) static void trap(void)
{
    for (;;) { }
}

/* All interrupts remain disabled until the bootloader selects its table. */
const uintptr_t r1_mbr_vectors[128]
    __attribute__((section(".isr_vector"), aligned(512), used)) = {
    [0] = 0x20001000u,
    [1] = (uintptr_t)Reset_Handler,
    [2 ... 127] = (uintptr_t)trap,
};

const uint32_t r1_mbr_config_words[2]
    __attribute__((section(".mbr_config"), used)) = {
    R1_MBR_BOOTLOADER_BASE, R1_MBR_COPY_PAGE,
};
