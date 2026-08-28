/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded source replacement for the G2 2.2.6.10 runtime byte-span emitter
 * at 0x00482684. The exact stock boundary, five callers, indirect callback
 * ABI, context offsets, and negative topology are pinned by its standalone
 * host test.
 */

typedef unsigned int open_cfw_runtime_emit_word;

typedef open_cfw_runtime_emit_word (*open_cfw_runtime_emit_callback)(
    open_cfw_runtime_emit_word output_state,
    open_cfw_runtime_emit_word byte_value
);

struct open_cfw_runtime_emit_context {
    open_cfw_runtime_emit_word reserved_00;
    open_cfw_runtime_emit_word reserved_04;
    open_cfw_runtime_emit_word output_state;
    open_cfw_runtime_emit_word reserved_0c;
    open_cfw_runtime_emit_word reserved_10;
    open_cfw_runtime_emit_word reserved_14;
    open_cfw_runtime_emit_word reserved_18;
    open_cfw_runtime_emit_word reserved_1c;
    open_cfw_runtime_emit_word reserved_20;
    open_cfw_runtime_emit_word reserved_24;
    open_cfw_runtime_emit_word reserved_28;
    open_cfw_runtime_emit_word emitted_count;
};

_Static_assert(
    sizeof(open_cfw_runtime_emit_word) == 4U,
    "runtime-emitter word width changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_emit_context,
        output_state
    ) == 0x08U,
    "runtime-emitter output-state offset changed"
);
_Static_assert(
    __builtin_offsetof(
        struct open_cfw_runtime_emit_context,
        emitted_count
    ) == 0x2cU,
    "runtime-emitter count offset changed"
);

__attribute__((used, noinline))
int open_cfw_runtime_emit_span(
    open_cfw_runtime_emit_callback callback,
    struct open_cfw_runtime_emit_context *context,
    const unsigned char *source,
    open_cfw_runtime_emit_word length
)
{
    while (length != 0U) {
        open_cfw_runtime_emit_word output_state =
            callback(context->output_state, (open_cfw_runtime_emit_word)*source);

        context->output_state = output_state;
        if (output_state == 0U) {
            return -1;
        }

        context->emitted_count += 1U;
        source += 1U;
        length -= 1U;
    }

    return 0;
}
