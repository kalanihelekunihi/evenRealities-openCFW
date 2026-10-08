# Full CapSense initialization, request flags and driver capture

**722 comparisons passed** for original initialization/capture/mode instructions against independent source and unmodified public PDL capture. No function-entry stubs. Cases include null context, prior modes 0–8/255, driver locks 0/1/2/255, null/non-null hardware base, zero/mixed/nonzero maxima and existing status flags 0/1/255. Internal fields, all three widget contexts, lock and status match.

Initialization first resets internal fields, enables widgets and requests measurement for zero maxima. It then switches to mode 0. An invalid previous mode aborts with error 1 **after those field changes**.

The capture wrapper returns `0x80` for any nonzero driver lock, including already-owned CapSense key 2. With an unlocked driver, public capture either fails (mapped to 8, such as a null hardware base) or stores key 2 and installs default mode 1. Initialization does not itself measure maximum count or acquire samples; downstream enable flow performs measurement.

Zero column/row maxima add request bits 8/16. Nonzero maxima do not clear existing request bits. Widget contexts are contiguous 60-byte records from the first widget's context pointer. Initialization failure has no rollback; a repeated call can alter prepared fields/mode before reporting a lock error.

Driver capture `0x8fa0` is **48 bytes exactly reproduced** from pinned public PDL with Arm GNU 13.3 `-Og`. This does not uniquely identify the producer/compiler or establish whole-firmware equality. Source: `mode_offline/capture.c` and `init.c`. Locks/configurations are synthetic; no hardware or concurrency claim.
