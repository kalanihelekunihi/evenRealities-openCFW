/*
 * SPDX-License-Identifier: MIT
 *
 * Source replacement for the G2 2.2.6.10 bounded string-length veneer at
 * 0x00454770...0x00454777.
 *
 * Valid-string behavior matches mpaland/printf _strnlen_s at commit
 * d3b984684bb8a8bdc48cc7a1abecb93ce59bbe3e. The stock veneer delegates to
 * the optimized routine at 0x0048D4E8, which additionally proves that a null
 * string returns zero and a zero maximum performs no string load.
 */

typedef __UINT32_TYPE__ open_cfw_runtime_strnlen_s_word;

_Static_assert(
    sizeof(open_cfw_runtime_strnlen_s_word) == 4U,
    "bounded string-length word width changed"
);

open_cfw_runtime_strnlen_s_word open_cfw_runtime_bounded_string_length(
    const char *string,
    open_cfw_runtime_strnlen_s_word maximum_length
);

__attribute__((used, noinline, minsize))
open_cfw_runtime_strnlen_s_word open_cfw_runtime_strnlen_s(
    const char *string,
    open_cfw_runtime_strnlen_s_word maximum_length
)
{
    return open_cfw_runtime_bounded_string_length(string, maximum_length);
}
