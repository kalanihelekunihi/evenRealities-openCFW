/*
 * SPDX-License-Identifier: MIT
 *
 * Host-testable decision boundary from the G2 2.2.6.10 lens-side
 * initialization routine.
 */

/*
 * Five matching readings publish side 2 when the hardware value is 1 and
 * side 1 for every other value. Any mismatch returns the unavailable value 3.
 */
__attribute__((used, noinline))
unsigned int open_cfw_classify_lens_samples(
    const unsigned int samples[5]
)
{
    unsigned int index;

    for (index = 1; index < 5; ++index) {
        if (samples[index] != samples[0]) {
            return 3;
        }
    }
    return samples[0] == 1U ? 2U : 1U;
}
