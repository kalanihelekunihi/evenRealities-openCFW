/*
 * SPDX-License-Identifier: FTL
 *
 * Bounded import providers for the isolated FreeType 2.9.1 CFF placement.
 * The FreeType property and stream routines preserve the VER-2-9-1 behavior;
 * the small ISO C routines are allocation-free and avoid target libc drift.
 */

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_MODULE_H
#include FT_INTERNAL_OBJECTS_H
#include FT_INTERNAL_STREAM_H
#include FT_SERVICE_PROPERTIES_H

#include <stddef.h>
#include <string.h>

#undef memcpy
#undef memset

static FT_Error open_cfw_freetype_cff_property_do(
    FT_Library library,
    const FT_String *module_name,
    const FT_String *property_name,
    void *value,
    FT_Bool set
)
{
    FT_Module *current;
    FT_Module *limit;
    FT_Module_Interface interface;
    FT_Service_Properties service;

    if (library == NULL) {
        return FT_Err_Invalid_Library_Handle;
    }
    if (module_name == NULL || property_name == NULL || value == NULL) {
        return FT_Err_Invalid_Argument;
    }
    current = library->modules;
    limit = current + library->num_modules;
    while (current < limit) {
        if (strcmp(current[0]->clazz->module_name, module_name) == 0) {
            break;
        }
        ++current;
    }
    if (current == limit) {
        return FT_Err_Missing_Module;
    }
    if (current[0]->clazz->get_interface == NULL) {
        return FT_Err_Unimplemented_Feature;
    }
    interface = current[0]->clazz->get_interface(
        current[0], FT_SERVICE_ID_PROPERTIES
    );
    if (interface == NULL) {
        return FT_Err_Unimplemented_Feature;
    }
    service = (FT_Service_Properties)interface;
    if (set) {
        if (service->set_property == NULL) {
            return FT_Err_Unimplemented_Feature;
        }
        return service->set_property(
            current[0], property_name, value, 0
        );
    }
    if (service->get_property == NULL) {
        return FT_Err_Unimplemented_Feature;
    }
    return service->get_property(current[0], property_name, value);
}

FT_Error FT_Property_Set(
    FT_Library library,
    const FT_String *module_name,
    const FT_String *property_name,
    const void *value
)
{
    return open_cfw_freetype_cff_property_do(
        library, module_name, property_name, (void *)value, 1
    );
}

FT_Error FT_Property_Get(
    FT_Library library,
    const FT_String *module_name,
    const FT_String *property_name,
    void *value
)
{
    return open_cfw_freetype_cff_property_do(
        library, module_name, property_name, value, 0
    );
}

FT_ULong FT_Stream_Pos(FT_Stream stream)
{
    return stream->pos;
}

int memcmp(const void *first, const void *second, size_t count)
{
    const unsigned char *left = (const unsigned char *)first;
    const unsigned char *right = (const unsigned char *)second;

    while (count != 0U) {
        if (*left != *right) {
            return (int)*left - (int)*right;
        }
        ++left;
        ++right;
        --count;
    }
    return 0;
}

void *memcpy(void *destination, const void *source, size_t count)
{
    unsigned char *output = (unsigned char *)destination;
    const unsigned char *input = (const unsigned char *)source;
    size_t index;

    for (index = 0U; index < count; ++index) {
        output[index] = input[index];
    }
    return destination;
}

void *memset(void *destination, int value, size_t count)
{
    unsigned char *output = (unsigned char *)destination;
    unsigned char byte = (unsigned char)value;

    while (count != 0U) {
        *output++ = byte;
        --count;
    }
    return destination;
}

int strcmp(const char *first, const char *second)
{
    const unsigned char *left = (const unsigned char *)first;
    const unsigned char *right = (const unsigned char *)second;

    while (*left != 0U && *left == *right) {
        ++left;
        ++right;
    }
    return (int)*left - (int)*right;
}

size_t strlen(const char *text)
{
    const char *cursor = text;

    while (*cursor != '\0') {
        ++cursor;
    }
    return (size_t)(cursor - text);
}

int strncmp(const char *first, const char *second, size_t count)
{
    const unsigned char *left = (const unsigned char *)first;
    const unsigned char *right = (const unsigned char *)second;

    while (count != 0U) {
        if (*left != *right) {
            return (int)*left - (int)*right;
        }
        if (*left == 0U) {
            return 0;
        }
        ++left;
        ++right;
        --count;
    }
    return 0;
}

char *strstr(const char *text, const char *needle)
{
    size_t needle_length = strlen(needle);

    if (needle_length == 0U) {
        return (char *)text;
    }
    while (*text != '\0') {
        if (*text == *needle && strncmp(text, needle, needle_length) == 0) {
            return (char *)text;
        }
        ++text;
    }
    return NULL;
}
