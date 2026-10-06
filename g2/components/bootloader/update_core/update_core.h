/* SPDX-License-Identifier: MIT */
#ifndef OPENCFW_BOOT_UPDATE_CORE_H
#define OPENCFW_BOOT_UPDATE_CORE_H
#include <stdint.h>
#include <stddef.h>
typedef struct {
    uint32_t encoded_size, expected_crc, reserved8, reserved12;
    uint32_t version_word, destination, reserved24, reserved28;
} opencfw_boot_image_header;
typedef struct {
    uint32_t unknown0, chunk_size, unknown8, unknown12, unknown16, unknown20;
    void (*read)(void *out, uint32_t address, uint32_t size);
    void (*program)(uint32_t address, const void *data, uint32_t size);
    void (*erase)(uint32_t address);
} opencfw_boot_storage;
uint32_t opencfw_boot_crc32(const void *, uint32_t, const uint32_t *);
uintptr_t opencfw_boot_stream_mode(uint32_t);
int32_t opencfw_boot_memcmp(const void *, const void *, uint32_t);
void opencfw_boot_erase_visit(uint32_t, uint32_t);
int32_t opencfw_boot_compare(uint32_t, const void *, uint32_t, const opencfw_boot_storage *);
uint32_t opencfw_boot_verify(uint32_t *, const opencfw_boot_image_header *);
void opencfw_boot_program(uint32_t *, const opencfw_boot_image_header *);
_Noreturn void opencfw_boot_vector_handoff(uint32_t);
/* Recovered provider ABIs, incomplete platform integration. The ELF test link
 * binds these explicit symbols to stock entry addresses for observation only.
 * No provider executable bytes are retained in the compiled source ELF. */
uint32_t opencfw_boot_file_open(uintptr_t path, uintptr_t mode);
uint32_t opencfw_boot_file_prepare(uint32_t handle, uint32_t offset, uint32_t mode);
uint32_t opencfw_boot_file_read(void *, uint32_t element_size, uint32_t count, uint32_t handle);
uint32_t opencfw_boot_file_close(uint32_t handle);
void opencfw_boot_runtime_call(uint32_t, uint32_t);
void opencfw_boot_log(uint32_t severity, uintptr_t tag, uintptr_t file,
                      uintptr_t function, uint32_t line, uintptr_t format, ...);
#endif
