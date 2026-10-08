# Independent review — P2-21407

Status: partial; accepted: false.

Fresh replay passed for the 100-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The preceding path stores the wrapping size difference before updating the resource counter, independently reloads current and high-water values for the unsigned selection, and follows the release helper and return sequence shown. In the new routine, the resource-null and request-result guards precede size handling. The size helper runs before a fresh counter read; the unsigned comparison branches on the resulting size, and the subtraction path uses a later fresh counter read with wrapping arithmetic.

Branch continuations and external helper contracts remain unresolved. Review remains partial/unaccepted.
