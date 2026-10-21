# Stock-adapted radio/WSF handoff

This component replaces the radio event-submission fixture in the combined `wsf-radio-simulator` target. Real reconstructed WSF event accumulation, byte critical nesting, ISR/task wake decision, dispatcher and radio/GPIO code execute. The older radio-only simulator retains its own historical scheduler fixture. The new target excludes that fixture object and links this component's adapter.

The C follows pinned public Apache-2.0 WSF semantics, adapted to authenticated stock machine code. It is not unchanged public source, private Ambiq port source, compiler-byte equality or a complete RTOS implementation. Exact public commit, Gitblob identities, notices and differences are in SOURCE_PROVENANCE.json and LICENSE.md. Public WSF uses16-bit events/default16 handlers; stock uses8-bit event slots and10 handlers in a64-byte control block. The interface describes this recovered stock ABI rather than substituting public defaults.

`make -C g2 wsf-radio-simulator` builds the callable ARM32 target. `make -C g2 wsf-radio-simulator-test WSF_SIM_REPORT=build/foundation/wsf-radio-simulator/new-comparison.json` runs original/source comparisons (fresh output path required). Native execution of installed OpenCFW Python/Unicorn is required on this host.

The provider functions in simulator/providers.c are synthetic RTOS/context/timer/queue fixtures. Production integration must replace them with real providers preserving the recovered call ABI, including the five-argument wait call. The functions are named by recovered role; no complete proprietary FreeRTOS wrapper identity or published C type claim is made. Application handler pointers/messages also require actual initialized providers and valid lifetimes.

Events OR together and truncate to8bits. IDs mask to low4bits without validation: callers use initialized IDs0..9. Invalid slots10/11 hit padding;12..15 hit queue-head bytes. Zero masks still set task flag4 and wake. Outermost WSF critical exit enables IRQs instead of restoring prior PRIMASK; callers must obey balanced nesting, with IRQs masked while already nested. Overflow/underflow cases are reproduced, not made safe.

Dispatcher order is message callbacks→message free, timer callbacks, then event callbacks in ascending ID order. Event slots clear before callback; same-ID reposting is handled in a later drain pass. Missing handler pointers leave their event byte intact even when task flags clear. Disable of GPIO117 does not clear an already-pending WSF event or cancel queued work. Physical scheduling, concurrency/quiescence and RTOS queue/allocator ownership remain unverified.

See ../../../analysis/wsf-radio-handoff-2026-10-05/REPORT.md for fresh comparisons, original evidence and limits.
