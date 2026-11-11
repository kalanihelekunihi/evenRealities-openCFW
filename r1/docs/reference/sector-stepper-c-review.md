# R1 sector-reader control in C

The later [FAL integration review](sector-fal-integration-review.md) corrects
header-call R6 leakage and expands the adapter to 100 bytes. It also records
a full stock/source helper-frame counterexample beyond this modeled boundary.
The following describes the earlier stepper round.

The sector reader at `0x87c24` now uses C for all read selection, traversal,
diagnostic sequencing, assertion selection and return policy. The prior
228-byte assembly scaffold is replaced by an 88-byte stack/ABI adapter.
Header preparation and traversal-update C workers are byte unchanged.

The adapter calls a C stepper with a private 28-byte call plan. The stepper
returns before a provider runs. The adapter loads the requested arguments,
restores the original stack position, calls the provider and carries its R0
into the next step. The first header-read result is deliberately ignored:
the original flash address must survive until header preparation.

The outer native frame remains 128 bytes. Its 104-byte local view starts at
caller `SP-128`; nested TSL reads still use caller `SP-176`. A temporary
96-byte reservation below the outer frame holds C arguments, plan and a
protected 48-byte region. No C frame or plan remains active during provider
execution. The adapter implements only this protocol, frame restoration and
the native assertion loop; storage decisions live in C.

Retained REA evidence observes the complete 360-byte stock body through
`0x87d8b`. Its subject hash was revalidated, and the analysis ELF text was
checked against the locked application with SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.
No new pseudocode coverage or global gate credit is inferred.

[Machine-readable evidence](sector-stepper-c-review.json) records 12,302
paired stock/C cases: 11,856 return cases, 206 native assertion cases and
240 bounded 16-read prefixes for very long corrupt-size traversals. Checks
cover header/status combinations, partial and non-writing reads, aliased
views, wrapping bounds, diagnostics, ordered shared accesses, outer-frame
and nested-buffer bytes, return value, saved registers, SP and masks.

Entry hooks explicitly check the native outer SP for header reads, nested
TSL calls, path getters and printf calls. Extra cases mutate database state,
traversal fields, names and diagnostic arguments during provider calls,
including the final error cleanup. Losing the original flash address and
calling a provider before restoring SP are both rejected.

The actual C stepper, preparation/update workers, read adapter, status scanner
and TSL control execute. Partition reads, printf and the path getter are
modeled. Helper-private frames and temporary unused/saved words between the
nested raw view and outer scratch are excluded. The bounded-prefix fixtures
do not establish eventual termination. Full FAL/device operation, physical
flash, concurrency, arbitrary corruption and unused caller-clobbered register
or flag values remain unproven.

All other 574 objects, the existing function-name data owner, manifest and
composed import sets are unchanged. All 575 R1 units compile without failures
or duplicate strong symbols; imports remain 175 application and 34 bootloader.
`make sources-check` passes. Five qualification variants compile, but none
selects an exact region. The canonical plan is unchanged at 3,881 source-built
application bytes, 642,279 binary pull-through bytes and 248 resource bytes.
The fresh hybrid application equals stock, with source completeness false.

Complete source linking and a byte-identical full-source rebuild remain
outstanding. No G2 gate advances; the goal remains active.
