# EM9305 prepared initializer lowers

This directory is a prepared source candidate. It does **not** modify the
selected `g2/components/em9305/qpc_scheduler_candidate/controller_init.c`,
shared build manifest, or the parent receipts.

## Provenance and scope

The instruction source is
`g2/build/c-firmware/20261011/em-inspection-full.arcem.txt`, decoded from
authenticated `em-activation-round/em-inspection.bin` at base `0x302400`
(SHA-256 `0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03`).
This pass reduces full native envelopes `0x306c44..0x306c7a`,
`0x3077f4..0x307832`, `0x307834..0x30789e`, `0x3079c4..0x307a16`,
`0x307af8..0x307b5e`, two stream initialization children
`0x307980..0x3079c2` and `0x307a68..0x307af6`, product buffer clear
`0x317498..0x3174d6`, prelink registration/state `0x3078a0..0x30796e`, and two leaf callbacks
`0x307a18..0x307a24` and `0x307b60..0x307b6c`. Typed callback identities
are genuine source-link contracts, not stock numeric code addresses. All
four direct lower children and both deeper service calls (`0x3251dc`,
`0x318ab8`) are now prepared source bodies. Direct native callback aliases
`0x30fc20`, `0x30fc24`, `0x31d438`, `0x320084`, and the three-call
`0x32056c` are in `init_callback_aliases.c`; the latter binds existing
selected `common_init_303d18` and `common_init_302ec8` providers.
The `0x31369c` 144-byte clear and `0x31e604` ordered callback chain are
prepared in `init_callback_chain.c`, with selected source callees retained
as named external symbols.
Both stream children use the already selected native-derived
`opencfw_em9305_memset` provider; the selected controller also already has
the first table's three record addresses and bit/config helpers, so these
are not redefined in the selected source.

The native code installs code pointers into RAM, reads the product-version
byte via `*[0x805cac]+4`, conditionally sets state bits, and executes a
halfword store in a return delay slot. The source preserves those state
and read-order boundaries. The existing `controller_init.c` forwarding
wrappers pass/return `uint32_t`; these prepared bodies retain that ABI.
The output values at exits come from the decoded R0 dataflow, including
the address return on the `0x3077f4` high-version branch.

## Verification

The ten source units compile and relocatably link with the pinned
ARC GNU 2026.03 CK/EM toolchain, `-mcpu=arcem -mcode-density -O2 -Wall
-Wextra -Werror`. The resulting object has 19 unresolved callback bodies
and six selected provider imports; no fixed executable address is inserted
as a pointer value.

An independent Linux host harness maps the authenticated RAM/data address
regions and runs all five bodies for every 8-bit product version (256
states), checking callback registrations, flags, halfwords, R0 outputs,
and child-call ordering. It also checks the two source callback leaves
against mapped product table entries, including the 704-byte stream clears
and 124-byte secondary context clear. Result:
`PASS 256 version states across five full lower bodies and four children`.
The same host run checks the two alias mode registrations, tail-call return
values, and the `0x32056c` sequence with its selected source children.
Both three-entry stream tables are checked for context index bytes 0, 1,
and 2. The first stream child is also checked with one, two, and three
null entries, including its native R0 fallbacks. Native `stb_s` at
`0x3079ba` and `0x307aa0` stores the running index; an earlier prepared
version incorrectly stored zero for all entries and is superseded.
Target disassembly of corrected `0x306c44` also confirms its first state
load precedes the second callback store, as the native instruction order
requires; the original prepared version had these two operations reversed.
This is a bounded source/native-instruction contract fixture, not an ARC
native-vs-C emulator equivalence or device qualification.

## Integration boundary

Compile `init_registration.c`, `init_mode.c`, `init_stream_children.c`,
`init_product_buffers.c`, `init_prelink.c`, `init_deeper_services.c`,
`init_callback_aliases.c`, `init_callback_chain.c`, and
`init_callback_status.c`
as distinct units. The integration owner should first bind each named
callback to its actual selected source body or retain its unresolved import.
The current `ld -r` graph has 19 remaining callback body identities and
six known selected provider imports (`common_init_302ec8`,
`common_init_302ff4`, `common_init_303008`, `common_init_303d18`,
`init_lower_30e42c`, and `memset`). Do not resolve remaining callbacks
with raw stock addresses.
The native 32-bit table at `0x3357a8`/`0x3357b4` remains initialized
product data and needs a final scatter/data owner.
