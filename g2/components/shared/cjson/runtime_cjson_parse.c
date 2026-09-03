/*
 * SPDX-License-Identifier: MIT
 *
 * G2 production parse-side cJSON runtime.
 *
 * This translation unit is a bounded adaptation of Dave Gamble's cJSON
 * v1.7.12 parse implementation (commit
 * 3c8935676a97c7c97bf006db8312875b4f292f6c).  It preserves the linked G2
 * cJSON 1.7.9--1.7.12 data model and parsing behavior while replacing the
 * compiler-library helpers with freestanding C.  The target build binds the
 * allocator hooks and error record to their authenticated stock SRAM ABI.
 */

#include "cJSON.h"

#ifdef true
#undef true
#endif
#define true ((cJSON_bool)1)

#ifdef false
#undef false
#endif
#define false ((cJSON_bool)0)

#define OPEN_CFW_CJSON_HOOKS_ADDRESS ((uintptr_t)0x2007410CU)
#define OPEN_CFW_CJSON_ERROR_ADDRESS ((uintptr_t)0x200004BCU)
#define OPEN_CFW_CJSON_INT_MAX 2147483647
#define OPEN_CFW_CJSON_INT_MIN (-OPEN_CFW_CJSON_INT_MAX - 1)

typedef struct
{
    const unsigned char *json;
    size_t position;
} error;

typedef struct
{
    void *(CJSON_CDECL *allocate)(size_t size);
    void (CJSON_CDECL *deallocate)(void *pointer);
    void *(CJSON_CDECL *reallocate)(void *pointer, size_t size);
} internal_hooks;

#if defined(OPEN_CFW_CJSON_G2)
typedef __UINTPTR_TYPE__ uintptr_t;

static inline internal_hooks *open_cfw_cjson_hooks(void)
{
    return (internal_hooks *)OPEN_CFW_CJSON_HOOKS_ADDRESS;
}

static inline error *open_cfw_cjson_error(void)
{
    return (error *)OPEN_CFW_CJSON_ERROR_ADDRESS;
}
#else
#include <stdlib.h>

typedef __UINTPTR_TYPE__ uintptr_t;
static internal_hooks open_cfw_cjson_host_hooks = { malloc, free, realloc };
static error open_cfw_cjson_host_error = { NULL, 0U };

static inline internal_hooks *open_cfw_cjson_hooks(void)
{
    return &open_cfw_cjson_host_hooks;
}

static inline error *open_cfw_cjson_error(void)
{
    return &open_cfw_cjson_host_error;
}
#endif

typedef struct
{
    const unsigned char *content;
    size_t length;
    size_t offset;
    size_t depth;
    internal_hooks hooks;
} parse_buffer;

#define can_read(buffer, size) \
    (((buffer) != NULL) && (((buffer)->offset + (size)) <= (buffer)->length))
#define can_access_at_index(buffer, index) \
    (((buffer) != NULL) && (((buffer)->offset + (index)) < (buffer)->length))
#define cannot_access_at_index(buffer, index) \
    (!can_access_at_index((buffer), (index)))
#define buffer_at_offset(buffer) ((buffer)->content + (buffer)->offset)

#if defined(__clang__) || defined(__GNUC__)
#define OPEN_CFW_ALWAYS_INLINE __attribute__((always_inline)) inline
#define OPEN_CFW_NOINLINE __attribute__((noinline))
#else
#define OPEN_CFW_ALWAYS_INLINE inline
#define OPEN_CFW_NOINLINE
#endif

static OPEN_CFW_ALWAYS_INLINE void open_cfw_zero(void *destination, size_t size)
{
    unsigned char *cursor = (unsigned char *)destination;
    while (size != 0U)
    {
        *cursor++ = 0U;
        size--;
    }
}

static OPEN_CFW_ALWAYS_INLINE size_t open_cfw_strlen(const char *string)
{
    const char *cursor = string;
    while (*cursor != '\0')
    {
        cursor++;
    }
    return (size_t)(cursor - string);
}

static OPEN_CFW_ALWAYS_INLINE int open_cfw_ascii_tolower(unsigned char value)
{
    if ((value >= (unsigned char)'A') && (value <= (unsigned char)'Z'))
    {
        return (int)(value + ((unsigned char)'a' - (unsigned char)'A'));
    }
    return (int)value;
}

static OPEN_CFW_ALWAYS_INLINE int open_cfw_strcmp(
    const unsigned char *left,
    const unsigned char *right)
{
    while ((*left != 0U) && (*left == *right))
    {
        left++;
        right++;
    }
    return (int)*left - (int)*right;
}

static OPEN_CFW_ALWAYS_INLINE double open_cfw_positive_infinity(void)
{
    union
    {
        unsigned long long bits;
        double value;
    } number = { 0x7FF0000000000000ULL };
    return number.value;
}

/*
 * Parse the decimal grammar consumed by strtod in the upstream parse_number
 * call.  The input is already restricted to 63 bytes from [0-9+-.eE].  An
 * incomplete exponent is deliberately not consumed, matching strtod.
 */
static OPEN_CFW_ALWAYS_INLINE cJSON_bool open_cfw_parse_decimal(
    const unsigned char *text,
    size_t length,
    double *result,
    size_t *consumed)
{
    size_t index = 0U;
    size_t exponent_marker = 0U;
    unsigned int digit_count = 0U;
    unsigned int fractional_digits = 0U;
    int negative = 0;
    int exponent_negative = 0;
    int exponent = 0;
    double value = 0.0;

    if ((index < length) && ((text[index] == '+') || (text[index] == '-')))
    {
        negative = (text[index] == '-');
        index++;
    }

    while ((index < length) && (text[index] >= '0') && (text[index] <= '9'))
    {
        value = (value * 10.0) + (double)(text[index] - '0');
        digit_count++;
        index++;
    }

    if ((index < length) && (text[index] == '.'))
    {
        index++;
        while ((index < length) && (text[index] >= '0') &&
               (text[index] <= '9'))
        {
            value = (value * 10.0) + (double)(text[index] - '0');
            digit_count++;
            fractional_digits++;
            index++;
        }
    }

    if (digit_count == 0U)
    {
        return false;
    }

    exponent_marker = index;
    if ((index < length) && ((text[index] == 'e') || (text[index] == 'E')))
    {
        size_t exponent_digits;
        index++;
        if ((index < length) && ((text[index] == '+') || (text[index] == '-')))
        {
            exponent_negative = (text[index] == '-');
            index++;
        }
        exponent_digits = index;
        while ((index < length) && (text[index] >= '0') &&
               (text[index] <= '9'))
        {
            if (exponent < 10000)
            {
                exponent = (exponent * 10) + (int)(text[index] - '0');
            }
            index++;
        }
        if (index == exponent_digits)
        {
            index = exponent_marker;
            exponent = 0;
            exponent_negative = 0;
        }
    }

    if (exponent_negative)
    {
        exponent = -exponent;
    }
    exponent -= (int)fractional_digits;

    if (value == 0.0)
    {
        /* A large exponent must not turn an exact zero into infinity. */
    }
    else if (exponent > 308)
    {
        value = open_cfw_positive_infinity();
    }
    else if (exponent < -400)
    {
        value = 0.0;
    }
    else
    {
        int remaining = exponent;
        while (remaining > 0)
        {
            value *= 10.0;
            remaining--;
        }
        while (remaining < 0)
        {
            value /= 10.0;
            remaining++;
        }
    }

    *result = negative ? -value : value;
    *consumed = index;
    return true;
}

OPEN_CFW_NOINLINE int case_insensitive_strcmp(
    const unsigned char *string1,
    const unsigned char *string2)
{
    if ((string1 == NULL) || (string2 == NULL))
    {
        return 1;
    }
    if (string1 == string2)
    {
        return 0;
    }
    while (open_cfw_ascii_tolower(*string1) == open_cfw_ascii_tolower(*string2))
    {
        if (*string1 == '\0')
        {
            return 0;
        }
        string1++;
        string2++;
    }
    return open_cfw_ascii_tolower(*string1) - open_cfw_ascii_tolower(*string2);
}

OPEN_CFW_NOINLINE cJSON *cJSON_New_Item(const internal_hooks * const hooks)
{
    cJSON *node = (cJSON *)hooks->allocate(sizeof(cJSON));
    if (node != NULL)
    {
        open_cfw_zero(node, sizeof(cJSON));
    }
    return node;
}

OPEN_CFW_NOINLINE void cJSON_Delete(cJSON *item)
{
    cJSON *next;
    internal_hooks *hooks = open_cfw_cjson_hooks();
    while (item != NULL)
    {
        next = item->next;
        if (((item->type & cJSON_IsReference) == 0) && (item->child != NULL))
        {
            cJSON_Delete(item->child);
        }
        if (((item->type & cJSON_IsReference) == 0) &&
            (item->valuestring != NULL))
        {
            hooks->deallocate(item->valuestring);
        }
        if (((item->type & cJSON_StringIsConst) == 0) && (item->string != NULL))
        {
            hooks->deallocate(item->string);
        }
        hooks->deallocate(item);
        item = next;
    }
}

OPEN_CFW_NOINLINE unsigned char get_decimal_point(void)
{
    return (unsigned char)'.';
}

OPEN_CFW_NOINLINE cJSON_bool parse_number(
    cJSON * const item,
    parse_buffer * const input_buffer)
{
    unsigned char number_text[64];
    size_t input_count = 0U;
    size_t consumed = 0U;
    double number = 0.0;

    if ((input_buffer == NULL) || (input_buffer->content == NULL))
    {
        return false;
    }
    while ((input_count < (sizeof(number_text) - 1U)) &&
           can_access_at_index(input_buffer, input_count))
    {
        unsigned char character = buffer_at_offset(input_buffer)[input_count];
        if (((character >= '0') && (character <= '9')) || (character == '+') ||
            (character == '-') || (character == 'e') || (character == 'E') ||
            (character == get_decimal_point()))
        {
            number_text[input_count++] = character;
        }
        else
        {
            break;
        }
    }
    if (!open_cfw_parse_decimal(number_text, input_count, &number, &consumed))
    {
        return false;
    }

    item->valuedouble = number;
    if (number >= (double)OPEN_CFW_CJSON_INT_MAX)
    {
        item->valueint = OPEN_CFW_CJSON_INT_MAX;
    }
    else if (number <= (double)OPEN_CFW_CJSON_INT_MIN)
    {
        item->valueint = OPEN_CFW_CJSON_INT_MIN;
    }
    else
    {
        item->valueint = (int)number;
    }
    item->type = cJSON_Number;
    input_buffer->offset += consumed;
    return true;
}

OPEN_CFW_NOINLINE unsigned parse_hex4(const unsigned char * const input)
{
    unsigned int result = 0U;
    size_t index;
    for (index = 0U; index < 4U; index++)
    {
        if ((input[index] >= '0') && (input[index] <= '9'))
        {
            result += (unsigned int)input[index] - (unsigned int)'0';
        }
        else if ((input[index] >= 'A') && (input[index] <= 'F'))
        {
            result += 10U + (unsigned int)input[index] - (unsigned int)'A';
        }
        else if ((input[index] >= 'a') && (input[index] <= 'f'))
        {
            result += 10U + (unsigned int)input[index] - (unsigned int)'a';
        }
        else
        {
            return 0U;
        }
        if (index < 3U)
        {
            result <<= 4;
        }
    }
    return result;
}

OPEN_CFW_NOINLINE unsigned char utf16_literal_to_utf8(
    const unsigned char * const input_pointer,
    const unsigned char * const input_end,
    unsigned char **output_pointer)
{
    unsigned long codepoint;
    unsigned int first_code;
    const unsigned char *first_sequence = input_pointer;
    unsigned char utf8_length;
    unsigned char utf8_position;
    unsigned char sequence_length;
    unsigned char first_byte_mark = 0U;

    if ((input_end - first_sequence) < 6)
    {
        return 0U;
    }
    first_code = parse_hex4(first_sequence + 2);
    if ((first_code >= 0xDC00U) && (first_code <= 0xDFFFU))
    {
        return 0U;
    }
    if ((first_code >= 0xD800U) && (first_code <= 0xDBFFU))
    {
        const unsigned char *second_sequence = first_sequence + 6;
        unsigned int second_code;
        sequence_length = 12U;
        if (((input_end - second_sequence) < 6) ||
            (second_sequence[0] != '\\') || (second_sequence[1] != 'u'))
        {
            return 0U;
        }
        second_code = parse_hex4(second_sequence + 2);
        if ((second_code < 0xDC00U) || (second_code > 0xDFFFU))
        {
            return 0U;
        }
        codepoint = 0x10000UL +
            (((unsigned long)(first_code & 0x3FFU) << 10) |
             (unsigned long)(second_code & 0x3FFU));
    }
    else
    {
        sequence_length = 6U;
        codepoint = first_code;
    }

    if (codepoint < 0x80UL)
    {
        utf8_length = 1U;
    }
    else if (codepoint < 0x800UL)
    {
        utf8_length = 2U;
        first_byte_mark = 0xC0U;
    }
    else if (codepoint < 0x10000UL)
    {
        utf8_length = 3U;
        first_byte_mark = 0xE0U;
    }
    else if (codepoint <= 0x10FFFFUL)
    {
        utf8_length = 4U;
        first_byte_mark = 0xF0U;
    }
    else
    {
        return 0U;
    }

    for (utf8_position = (unsigned char)(utf8_length - 1U);
         utf8_position > 0U; utf8_position--)
    {
        (*output_pointer)[utf8_position] = (unsigned char)((codepoint | 0x80UL) & 0xBFUL);
        codepoint >>= 6;
    }
    (*output_pointer)[0] = (utf8_length > 1U)
        ? (unsigned char)((codepoint | first_byte_mark) & 0xFFUL)
        : (unsigned char)(codepoint & 0x7FUL);
    *output_pointer += utf8_length;
    return sequence_length;
}

OPEN_CFW_NOINLINE cJSON_bool parse_string(
    cJSON * const item,
    parse_buffer * const input_buffer)
{
    const unsigned char *input_pointer = buffer_at_offset(input_buffer) + 1;
    const unsigned char *input_end = input_pointer;
    unsigned char *output_pointer;
    unsigned char *output = NULL;
    size_t skipped_bytes = 0U;

    if (buffer_at_offset(input_buffer)[0] != '"')
    {
        goto fail;
    }
    while (((size_t)(input_end - input_buffer->content) < input_buffer->length) &&
           (*input_end != '"'))
    {
        if (*input_end == '\\')
        {
            if ((size_t)(input_end + 1 - input_buffer->content) >=
                input_buffer->length)
            {
                goto fail;
            }
            skipped_bytes++;
            input_end++;
        }
        input_end++;
    }
    if (((size_t)(input_end - input_buffer->content) >= input_buffer->length) ||
        (*input_end != '"'))
    {
        goto fail;
    }
    output = (unsigned char *)input_buffer->hooks.allocate(
        (size_t)(input_end - buffer_at_offset(input_buffer)) - skipped_bytes + 1U);
    if (output == NULL)
    {
        goto fail;
    }

    output_pointer = output;
    while (input_pointer < input_end)
    {
        if (*input_pointer != '\\')
        {
            *output_pointer++ = *input_pointer++;
        }
        else
        {
            unsigned char sequence_length = 2U;
            switch (input_pointer[1])
            {
                case 'b': *output_pointer++ = '\b'; break;
                case 'f': *output_pointer++ = '\f'; break;
                case 'n': *output_pointer++ = '\n'; break;
                case 'r': *output_pointer++ = '\r'; break;
                case 't': *output_pointer++ = '\t'; break;
                case '"':
                case '\\':
                case '/': *output_pointer++ = input_pointer[1]; break;
                case 'u':
                    sequence_length = utf16_literal_to_utf8(
                        input_pointer, input_end, &output_pointer);
                    if (sequence_length == 0U)
                    {
                        goto fail;
                    }
                    break;
                default: goto fail;
            }
            input_pointer += sequence_length;
        }
    }
    *output_pointer = '\0';
    item->type = cJSON_String;
    item->valuestring = (char *)output;
    input_buffer->offset = (size_t)(input_end - input_buffer->content) + 1U;
    return true;

fail:
    if (output != NULL)
    {
        input_buffer->hooks.deallocate(output);
    }
    if (input_pointer != NULL)
    {
        input_buffer->offset = (size_t)(input_pointer - input_buffer->content);
    }
    return false;
}

OPEN_CFW_NOINLINE parse_buffer *buffer_skip_whitespace(parse_buffer * const buffer)
{
    if ((buffer == NULL) || (buffer->content == NULL))
    {
        return NULL;
    }
    while (can_access_at_index(buffer, 0U) &&
           (buffer_at_offset(buffer)[0] <= 32U))
    {
        buffer->offset++;
    }
    if (buffer->offset == buffer->length)
    {
        buffer->offset--;
    }
    return buffer;
}

OPEN_CFW_NOINLINE parse_buffer *skip_utf8_bom(parse_buffer * const buffer)
{
    if ((buffer == NULL) || (buffer->content == NULL) || (buffer->offset != 0U))
    {
        return NULL;
    }
    if (can_access_at_index(buffer, 4U) &&
        (buffer_at_offset(buffer)[0] == 0xEFU) &&
        (buffer_at_offset(buffer)[1] == 0xBBU) &&
        (buffer_at_offset(buffer)[2] == 0xBFU))
    {
        buffer->offset += 3U;
    }
    return buffer;
}

OPEN_CFW_NOINLINE cJSON_bool parse_value(
    cJSON * const item,
    parse_buffer * const input_buffer);
OPEN_CFW_NOINLINE cJSON_bool parse_array(
    cJSON * const item,
    parse_buffer * const input_buffer);
OPEN_CFW_NOINLINE cJSON_bool parse_object(
    cJSON * const item,
    parse_buffer * const input_buffer);

OPEN_CFW_NOINLINE cJSON *cJSON_ParseWithOpts(
    const char *value,
    const char **return_parse_end,
    cJSON_bool require_null_terminated)
{
    parse_buffer buffer;
    cJSON *item = NULL;
    error *global_error = open_cfw_cjson_error();
    internal_hooks *global_hooks = open_cfw_cjson_hooks();

    open_cfw_zero(&buffer, sizeof(buffer));
    global_error->json = NULL;
    global_error->position = 0U;
    if (value == NULL)
    {
        goto fail;
    }
    buffer.content = (const unsigned char *)value;
    buffer.length = open_cfw_strlen(value) + 1U;
    buffer.hooks = *global_hooks;
    item = cJSON_New_Item(global_hooks);
    if (item == NULL)
    {
        goto fail;
    }
    if (!parse_value(item, buffer_skip_whitespace(skip_utf8_bom(&buffer))))
    {
        goto fail;
    }
    if (require_null_terminated)
    {
        buffer_skip_whitespace(&buffer);
        if ((buffer.offset >= buffer.length) ||
            (buffer_at_offset(&buffer)[0] != '\0'))
        {
            goto fail;
        }
    }
    if (return_parse_end != NULL)
    {
        *return_parse_end = (const char *)buffer_at_offset(&buffer);
    }
    return item;

fail:
    if (item != NULL)
    {
        cJSON_Delete(item);
    }
    if (value != NULL)
    {
        global_error->json = (const unsigned char *)value;
        if (buffer.offset < buffer.length)
        {
            global_error->position = buffer.offset;
        }
        else if (buffer.length > 0U)
        {
            global_error->position = buffer.length - 1U;
        }
        else
        {
            global_error->position = 0U;
        }
        if (return_parse_end != NULL)
        {
            *return_parse_end = value + global_error->position;
        }
    }
    return NULL;
}

OPEN_CFW_NOINLINE cJSON *cJSON_Parse(const char *value)
{
    return cJSON_ParseWithOpts(value, NULL, false);
}

OPEN_CFW_NOINLINE cJSON_bool parse_value(
    cJSON * const item,
    parse_buffer * const input_buffer)
{
    const unsigned char *text;
    if ((input_buffer == NULL) || (input_buffer->content == NULL))
    {
        return false;
    }
    text = buffer_at_offset(input_buffer);
    if (can_read(input_buffer, 4U) && (text[0] == 'n') && (text[1] == 'u') &&
        (text[2] == 'l') && (text[3] == 'l'))
    {
        item->type = cJSON_NULL;
        input_buffer->offset += 4U;
        return true;
    }
    if (can_read(input_buffer, 5U) && (text[0] == 'f') && (text[1] == 'a') &&
        (text[2] == 'l') && (text[3] == 's') && (text[4] == 'e'))
    {
        item->type = cJSON_False;
        input_buffer->offset += 5U;
        return true;
    }
    if (can_read(input_buffer, 4U) && (text[0] == 't') && (text[1] == 'r') &&
        (text[2] == 'u') && (text[3] == 'e'))
    {
        item->type = cJSON_True;
        item->valueint = 1;
        input_buffer->offset += 4U;
        return true;
    }
    if (can_access_at_index(input_buffer, 0U) &&
        (buffer_at_offset(input_buffer)[0] == '"'))
    {
        return parse_string(item, input_buffer);
    }
    if (can_access_at_index(input_buffer, 0U) &&
        ((buffer_at_offset(input_buffer)[0] == '-') ||
         ((buffer_at_offset(input_buffer)[0] >= '0') &&
          (buffer_at_offset(input_buffer)[0] <= '9'))))
    {
        return parse_number(item, input_buffer);
    }
    if (can_access_at_index(input_buffer, 0U) &&
        (buffer_at_offset(input_buffer)[0] == '['))
    {
        return parse_array(item, input_buffer);
    }
    if (can_access_at_index(input_buffer, 0U) &&
        (buffer_at_offset(input_buffer)[0] == '{'))
    {
        return parse_object(item, input_buffer);
    }
    return false;
}

OPEN_CFW_NOINLINE cJSON_bool parse_array(
    cJSON * const item,
    parse_buffer * const input_buffer)
{
    cJSON *head = NULL;
    cJSON *current_item = NULL;
    if (input_buffer->depth >= CJSON_NESTING_LIMIT)
    {
        return false;
    }
    input_buffer->depth++;
    if (buffer_at_offset(input_buffer)[0] != '[')
    {
        goto fail;
    }
    input_buffer->offset++;
    buffer_skip_whitespace(input_buffer);
    if (can_access_at_index(input_buffer, 0U) &&
        (buffer_at_offset(input_buffer)[0] == ']'))
    {
        goto success;
    }
    if (cannot_access_at_index(input_buffer, 0U))
    {
        input_buffer->offset--;
        goto fail;
    }
    input_buffer->offset--;
    do
    {
        cJSON *new_item = cJSON_New_Item(&input_buffer->hooks);
        if (new_item == NULL)
        {
            goto fail;
        }
        if (head == NULL)
        {
            current_item = head = new_item;
        }
        else
        {
            current_item->next = new_item;
            new_item->prev = current_item;
            current_item = new_item;
        }
        input_buffer->offset++;
        buffer_skip_whitespace(input_buffer);
        if (!parse_value(current_item, input_buffer))
        {
            goto fail;
        }
        buffer_skip_whitespace(input_buffer);
    }
    while (can_access_at_index(input_buffer, 0U) &&
           (buffer_at_offset(input_buffer)[0] == ','));
    if (cannot_access_at_index(input_buffer, 0U) ||
        (buffer_at_offset(input_buffer)[0] != ']'))
    {
        goto fail;
    }

success:
    input_buffer->depth--;
    item->type = cJSON_Array;
    item->child = head;
    input_buffer->offset++;
    return true;

fail:
    if (head != NULL)
    {
        cJSON_Delete(head);
    }
    return false;
}

OPEN_CFW_NOINLINE cJSON_bool parse_object(
    cJSON * const item,
    parse_buffer * const input_buffer)
{
    cJSON *head = NULL;
    cJSON *current_item = NULL;
    if (input_buffer->depth >= CJSON_NESTING_LIMIT)
    {
        return false;
    }
    input_buffer->depth++;
    if (cannot_access_at_index(input_buffer, 0U) ||
        (buffer_at_offset(input_buffer)[0] != '{'))
    {
        goto fail;
    }
    input_buffer->offset++;
    buffer_skip_whitespace(input_buffer);
    if (can_access_at_index(input_buffer, 0U) &&
        (buffer_at_offset(input_buffer)[0] == '}'))
    {
        goto success;
    }
    if (cannot_access_at_index(input_buffer, 0U))
    {
        input_buffer->offset--;
        goto fail;
    }
    input_buffer->offset--;
    do
    {
        cJSON *new_item = cJSON_New_Item(&input_buffer->hooks);
        if (new_item == NULL)
        {
            goto fail;
        }
        if (head == NULL)
        {
            current_item = head = new_item;
        }
        else
        {
            current_item->next = new_item;
            new_item->prev = current_item;
            current_item = new_item;
        }
        input_buffer->offset++;
        buffer_skip_whitespace(input_buffer);
        if (!parse_string(current_item, input_buffer))
        {
            goto fail;
        }
        buffer_skip_whitespace(input_buffer);
        current_item->string = current_item->valuestring;
        current_item->valuestring = NULL;
        if (cannot_access_at_index(input_buffer, 0U) ||
            (buffer_at_offset(input_buffer)[0] != ':'))
        {
            goto fail;
        }
        input_buffer->offset++;
        buffer_skip_whitespace(input_buffer);
        if (!parse_value(current_item, input_buffer))
        {
            goto fail;
        }
        buffer_skip_whitespace(input_buffer);
    }
    while (can_access_at_index(input_buffer, 0U) &&
           (buffer_at_offset(input_buffer)[0] == ','));
    if (cannot_access_at_index(input_buffer, 0U) ||
        (buffer_at_offset(input_buffer)[0] != '}'))
    {
        goto fail;
    }

success:
    input_buffer->depth--;
    item->type = cJSON_Object;
    item->child = head;
    input_buffer->offset++;
    return true;

fail:
    if (head != NULL)
    {
        cJSON_Delete(head);
    }
    return false;
}

OPEN_CFW_NOINLINE int cJSON_GetArraySize(const cJSON *array)
{
    const cJSON *child;
    size_t size = 0U;
    if (array == NULL)
    {
        return 0;
    }
    child = array->child;
    while (child != NULL)
    {
        size++;
        child = child->next;
    }
    return (int)size;
}

OPEN_CFW_NOINLINE cJSON *get_array_item(const cJSON *array, size_t index)
{
    cJSON *current_child;
    if (array == NULL)
    {
        return NULL;
    }
    current_child = array->child;
    while ((current_child != NULL) && (index > 0U))
    {
        index--;
        current_child = current_child->next;
    }
    return current_child;
}

OPEN_CFW_NOINLINE cJSON *cJSON_GetArrayItem(const cJSON *array, int index)
{
    if (index < 0)
    {
        return NULL;
    }
    return get_array_item(array, (size_t)index);
}

OPEN_CFW_NOINLINE cJSON *get_object_item(
    const cJSON * const object,
    const char * const name,
    const cJSON_bool case_sensitive)
{
    cJSON *current_element;
    if ((object == NULL) || (name == NULL))
    {
        return NULL;
    }
    current_element = object->child;
    if (case_sensitive)
    {
        while ((current_element != NULL) && (current_element->string != NULL) &&
               (open_cfw_strcmp((const unsigned char *)name,
                    (const unsigned char *)current_element->string) != 0))
        {
            current_element = current_element->next;
        }
    }
    else
    {
        while ((current_element != NULL) &&
               (case_insensitive_strcmp((const unsigned char *)name,
                    (const unsigned char *)current_element->string) != 0))
        {
            current_element = current_element->next;
        }
    }
    if ((current_element == NULL) || (current_element->string == NULL))
    {
        return NULL;
    }
    return current_element;
}

OPEN_CFW_NOINLINE cJSON *cJSON_GetObjectItem(
    const cJSON * const object,
    const char * const string)
{
    return get_object_item(object, string, false);
}

OPEN_CFW_NOINLINE cJSON_bool cJSON_IsArray(const cJSON * const item)
{
    if (item == NULL)
    {
        return false;
    }
    return ((item->type & 0xFF) == cJSON_Array) ? true : false;
}
