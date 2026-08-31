/* SPDX-License-Identifier: MIT */

#include <ft2build.h>
#include FT_FREETYPE_H
#include FT_MODULE_H
#include FT_INTERNAL_OBJECTS_H
#include FT_INTERNAL_STREAM_H
#include FT_SERVICE_PROPERTIES_H

#include <stddef.h>
#include <string.h>

static int stored_value;

static FT_Error fake_set(
    FT_Module module,
    const char *property_name,
    const void *value,
    FT_Bool value_is_string
)
{
    if (module == NULL || strcmp(property_name, "value") != 0 ||
        value == NULL || value_is_string != 0) {
        return FT_Err_Invalid_Argument;
    }
    stored_value = *(const int *)value;
    return FT_Err_Ok;
}

static FT_Error fake_get(
    FT_Module module,
    const char *property_name,
    void *value
)
{
    if (module == NULL || strcmp(property_name, "value") != 0 || value == NULL) {
        return FT_Err_Invalid_Argument;
    }
    *(int *)value = stored_value;
    return FT_Err_Ok;
}

static FT_Service_PropertiesRec fake_service = {
    fake_set,
    fake_get,
};

static FT_Module_Interface fake_interface(FT_Module module, const char *name)
{
    if (module != NULL && strcmp(name, FT_SERVICE_ID_PROPERTIES) == 0) {
        return &fake_service;
    }
    return NULL;
}

static int check_memory_and_strings(void)
{
    unsigned char source[] = {0x00, 0x7F, 0x80, 0xFF};
    unsigned char output[4];
    char text[12];

    memset(output, 0xA5, sizeof(output));
    if (output[0] != 0xA5 || output[3] != 0xA5) {
        return 1;
    }
    if (memcpy(output, source, sizeof(source)) != output ||
        memcmp(output, source, sizeof(source)) != 0 ||
        memcmp(source + 3, source + 2, 1) <= 0) {
        return 2;
    }
    memcpy(text, "open-cff", 9);
    if (strlen(text) != 8 || strcmp(text, "open-cff") != 0 ||
        strncmp(text, "open", 4) != 0 || strstr(text, "cff") != text + 5 ||
        strstr(text, "absent") != NULL || strstr(text, "") != text) {
        return 3;
    }
    return 0;
}

int main(void)
{
    FT_LibraryRec library = {0};
    FT_ModuleRec module = {0};
    FT_Module_Class clazz = {0};
    FT_StreamRec stream = {0};
    int input = 73;
    int output = 0;
    int status = check_memory_and_strings();

    if (status != 0) {
        return status;
    }
    stream.pos = 0x12345678UL;
    if (FT_Stream_Pos(&stream) != 0x12345678UL) {
        return 4;
    }
    clazz.module_name = "cff";
    clazz.get_interface = fake_interface;
    module.clazz = &clazz;
    module.library = &library;
    library.num_modules = 1;
    library.modules[0] = &module;
    if (FT_Property_Set(&library, "cff", "value", &input) != FT_Err_Ok ||
        FT_Property_Get(&library, "cff", "value", &output) != FT_Err_Ok ||
        output != input) {
        return 5;
    }
    if (FT_Property_Get(&library, "missing", "value", &output) !=
        FT_Err_Missing_Module) {
        return 6;
    }
    if (FT_Property_Set(NULL, "cff", "value", &input) !=
        FT_Err_Invalid_Library_Handle ||
        FT_Property_Get(&library, NULL, "value", &output) !=
        FT_Err_Invalid_Argument) {
        return 7;
    }
    return 0;
}
