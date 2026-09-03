/* SPDX-License-Identifier: MIT */

#include "cJSON.h"

#include <stdio.h>

static void emit_bytes(const char *value)
{
    const unsigned char *cursor = (const unsigned char *)value;
    if (cursor == NULL)
    {
        fputs("-", stdout);
        return;
    }
    while (*cursor != 0U)
    {
        printf("%02x", (unsigned int)*cursor++);
    }
}

static void emit_node(const cJSON *item)
{
    const cJSON *child;
    if (item == NULL)
    {
        fputs("X", stdout);
        return;
    }
    switch (item->type & 0xFF)
    {
        case cJSON_NULL: fputs("N", stdout); break;
        case cJSON_False: fputs("F", stdout); break;
        case cJSON_True: fputs("T", stdout); break;
        case cJSON_Number:
            printf("D(%d,%a)", item->valueint, item->valuedouble);
            break;
        case cJSON_String:
            fputs("S(", stdout);
            emit_bytes(item->valuestring);
            fputc(')', stdout);
            break;
        case cJSON_Array:
            fputc('[', stdout);
            for (child = item->child; child != NULL; child = child->next)
            {
                emit_node(child);
                if (child->next != NULL) fputc(',', stdout);
            }
            fputc(']', stdout);
            break;
        case cJSON_Object:
            fputc('{', stdout);
            for (child = item->child; child != NULL; child = child->next)
            {
                emit_bytes(child->string);
                fputc(':', stdout);
                emit_node(child);
                if (child->next != NULL) fputc(',', stdout);
            }
            fputc('}', stdout);
            break;
        default: printf("U(%d)", item->type & 0xFF); break;
    }
}

int main(int argc, char **argv)
{
    const char *end = NULL;
    cJSON *root;
    cJSON *named;
    if (argc != 2)
    {
        return 2;
    }
    root = cJSON_ParseWithOpts(argv[1], &end, 1);
    if (root == NULL)
    {
        puts("ERR");
        return 0;
    }
    emit_node(root);
    printf("|array=%d,size=%d", cJSON_IsArray(root), cJSON_GetArraySize(root));
    if (cJSON_IsArray(root))
    {
        fputs(",first=", stdout);
        emit_node(cJSON_GetArrayItem(root, 0));
    }
    named = cJSON_GetObjectItem(root, "name");
    fputs("|name=", stdout);
    emit_node(named);
    fputc('\n', stdout);
    cJSON_Delete(root);
    return 0;
}
