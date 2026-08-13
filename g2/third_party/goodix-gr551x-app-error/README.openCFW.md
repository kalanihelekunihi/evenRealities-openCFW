# Goodix GR551x application-error source oracle

This directory records the Goodix BLE SDK source behind the copied and locally
adapted G2 `utils/assert/util_error_check.c` utility. It is an analysis oracle,
not a Goodix BLE stack dependency and not production-routed OpenCFW code.

`upstream/app_error.c` is the byte-exact file preserved as
`GR551x_SDK_V1.7.0/components/libraries/app_error/app_error.c` in three public
SDK carriers. Its 43 error strings, 512-byte automatic buffer, two formatter
branches, and unbounded table walk match the stock G2 definition. The G2 copy
renames the handler, removes the never-reached fallback branch, and replaces
Goodix logging with the project logging seam.

No public official Goodix Git commit for the original SDK 1.7.0 distribution
was found. The selected commit in `PROVENANCE.json` is therefore the earliest
public carrier of the exact Git blob, not a claim about the private Even
checkout or the archive-producing Goodix commit.

The file's BSD-3-Clause terms are retained verbatim in its header.
