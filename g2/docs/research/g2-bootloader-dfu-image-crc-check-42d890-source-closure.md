# G2 bootloader DFU image CRC verifier source closure

The authenticated interval `[0x0042D890,0x0042D9F0)` is now production-routed
from `runtime_dfu_image_crc_check_42d890.c`. Apple clang 21 and Homebrew clang
22 reproduce the complete 352-byte stock body exactly after twelve strict
Thumb-call relocations. The sole direct caller is `0x0042DFF6`; no interior or
stored-pointer ingress exists. Eleven literal cells pin the DFU image path,
diagnostic context, read buffer/configuration, expected CRC state, and messages.

The service masks the encoded image size to 24 bits, skips the eight-byte
header, opens and prepares the image, reads every full configured chunk plus a
remainder, updates the table CRC after each read, logs short reads, closes and
clears the handle, reports calculated and expected CRC values, and returns their
equality. Portable tests cover invalid inputs, open failure, multiple full
chunks, remainder handling, a logged short read, CRC match, CRC mismatch, and
handle cleanup.

Offline compilation, portable behavior, provider identity, manifest ownership,
and unsigned firmware assembly are verified. Live filesystem contents, storage
I/O, buffer ownership, configuration state, logging, timing, corrupt/truncated
images, reset, and cold boot are blocked by unavailable physical evidence. No
signing, flashing, reset, or hardware access occurred, and functional
completeness is not claimed.
