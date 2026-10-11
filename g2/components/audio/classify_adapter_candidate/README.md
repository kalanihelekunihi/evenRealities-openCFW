# Experimental callback classify ABI adapter

The selected Apollo caller was rebuilt with the soft-float C ABI and passes
IEEE-754 bits in R0. The authenticated stock classify entry `0x5a1e8c`
accepts the float in S0. `alias.c` forwards the selected caller's C float to
the already selected source body `audio_platform_classify`; it introduces no
new algorithm or invented threshold.

A 24-case Unicorn suite compares stock S0 results against the retained C body
and a separately compiled softfp R0 adapter. Cases include all four range
boundaries, negative zero, infinities, subnormals and NaNs. It does not run
the entire platform callback/temperature path or establish FPSCR exception
side effects. The adapter remains outside the admitted 160-member archive.
