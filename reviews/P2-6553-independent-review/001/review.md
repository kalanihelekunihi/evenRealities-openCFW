# Independent review 6553

Disposition: **PASS_SCOPED**; `accepted:false`.

The source span 0x415E72..0x415F40 and packet hashes match. GNU decoding confirms the one-word path sign-extends the high word and the long-long path aligns and loads both words. Negative inputs are converted to a wrapped two-word magnitude and marked in R4; positive values are retained. With nonzero width, 415924 measures the magnitude, the sign is accounted for in the padding amount, and sign placement depends on the pad byte: zero padding emits `-` before the pad helper, space padding emits it after, while other pad bytes omit that sign on this width path. With zero width, a negative value emits the sign before calling 4159A0. The helper arguments come from the fresh magnitude stack slots, and output/count updates follow the null-output tests.

This is source-local flow only; it does not establish integer child behavior or general formatting expectations. No canonical files or gates changed.
