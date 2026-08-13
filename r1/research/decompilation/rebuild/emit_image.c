/* Generated exact-byte unsigned R1 image emitter. */
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const unsigned char r1_application[] = {
#include "application.bytes.inc"
};

static const unsigned char r1_bootloader[] = {
#include "bootloader.bytes.inc"
};

static const unsigned char r1_uicr[] = {
#include "uicr.bytes.inc"
};

static const unsigned char r1_approtect_runtime[] = {
#include "approtect-runtime.bytes.inc"
};

struct image_record {
    const char *name;
    const unsigned char *bytes;
    size_t size;
    const char *sha256;
};

static const struct image_record images[] = {
    {"application", r1_application, sizeof(r1_application), "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"},
    {"bootloader", r1_bootloader, sizeof(r1_bootloader), "566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b"},
    {"uicr", r1_uicr, sizeof(r1_uicr), "1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150"},
    {"approtect-runtime", r1_approtect_runtime, sizeof(r1_approtect_runtime), "fafdd44c03daf5f7ecfa57113ebd319de6fb8f84fa0b7b0c5ac60d09f811fb71"},
};

static void usage(const char *program) {
    fprintf(stderr, "usage: %s IMAGE OUTPUT\nimages:", program);
    for (size_t i = 0; i < sizeof(images) / sizeof(images[0]); ++i) {
        fprintf(stderr, " %s", images[i].name);
    }
    fputc('\n', stderr);
}

int main(int argc, char **argv) {
    if (argc != 3) {
        usage(argv[0]);
        return 64;
    }
    const struct image_record *selected = NULL;
    for (size_t i = 0; i < sizeof(images) / sizeof(images[0]); ++i) {
        if (strcmp(argv[1], images[i].name) == 0) {
            selected = &images[i];
            break;
        }
    }
    if (selected == NULL) {
        usage(argv[0]);
        return 64;
    }
    FILE *output = fopen(argv[2], "wb");
    if (output == NULL) {
        fprintf(stderr, "cannot open %s: %s\n", argv[2], strerror(errno));
        return 1;
    }
    size_t written = fwrite(selected->bytes, 1, selected->size, output);
    int close_result = fclose(output);
    if (written != selected->size || close_result != 0) {
        fprintf(stderr, "failed writing %s\n", argv[2]);
        return 1;
    }
    fprintf(stderr, "%s: %zu bytes; expected SHA-256 %s\n",
            selected->name, selected->size, selected->sha256);
    return 0;
}
