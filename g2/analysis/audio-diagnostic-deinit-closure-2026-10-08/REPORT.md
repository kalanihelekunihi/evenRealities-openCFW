# Diagnostic codec/PDM deinit: asynchronous control before owner gate

**64 PASS selected original/independent deinit comparisons**. Original0x58F74A (mode0) and0x58F806 (mode1) run actual queued-control, queue-copy/notification, owner-unregister and encoder-wrapper peers; independent C covers their first-party ordering and recording-stop prefix. File-close0x4745F4 and LC3-setup0x591374 are entry boundaries, never result stubs. [Source](../../components/audio/diagnostic_deinit_offline/deinit.c), [results](results.json).

## Actual order and ownership

Both functions **queue a disable control first**, then unregister owner0x10B for mode0/1. Message is twelve bytes **[type=mode,mode=1,value=0]**; successful queue submission sets audio thread flag0x400000. Tests execute real50×12 queue initialization/send and notification providers, comparing queued bytes/count and notification state. With queueNULL the actual submit wrapper returns without publication; deinit still performs owner-unregister. No consumer is scheduled by the fixture.

If registry callback is nonnull and belongs to a different owner, unregister returns−1; deinit returns that error, **but disable may already be queued**. This scoped behavior is not an observed hardware failure. A matching owner clears twelve registry bytes. An empty callback unregisters successfully without clearing stale owner/mode fields, then also proceeds to cleanup.

Success invokes recording stop for mode, followed by encoder setup. Recorder row is twelve bytes at0x20073C08+12*mode: file pointer+0 and active byte+10. Nonnull file reaches real file-close entry, so its later pointer clear/free is unexecuted. NULL file returns through the actual original recorder path and clears active byte before reaching encoder setup. Independent recorder prefix matches these effects; it does not model file lifetime after close.

Codec success statically sets up configurations0x20106A7C and0x201074C0; PDM success sets up0x20107F04. Tests stop at first LC3 setup call; second codec setup remains static continuation. No encoder initialization return, cached pointer update or hardware producer stop is fabricated.

## Authenticated diagnostic encoder records

The known compressed startup record0x75D404 was independently decoded again and compared against original decoder across **769,646 output bytes**. This is verification of an already-known startup region from the prior audio-stream analysis, **not newly discovered executable coverage**. New extraction identifies these diagnostic records:

| Address | Seven initial words |
| --- | --- |
| 0x20106A7C | 0,10000,16000,2,0,32000,0 |
| 0x201074C0 | 0,10000,16000,2,1,32000,0 |
| 0x20107F04 | 0,10000,16000,1,0,32000,0 |

The existing audio-stream field recovery interprets these as PCM-format selector, frame-duration argument, sample rate, channel stride/count, selected interleaved channel, bitrate and NULL cached encoder. Mode0 has two channel selections; mode1 has one. They differ from the previously mapped mono BLE record at0x20108948; they must not be merged into one assumed active configuration. Actual LC3 setup boundary receives10000/16000/0 and workspace configuration+28; duration/rate meanings inherit prior geometry evidence rather than a newly measured cadence.

Input extent0x78F6F7..0x79189E is8615 compressed bytes; output0x20080000..0x2013BE6E leaves **two bytes before BSS start0x2013BE70**. The guard check retains those bytes unchanged; no padding write/zero assumption is made. Startup-config-results.json gives full output hash and extracted words. No ignored decoded file is required.

Inputs: modes0/1, owners10B/999, empty/nonempty callback, queueNULL/present, recorderNULL/non-NULL, initial flags0/800000. Queue/task prefixes are constructed, nonwaiting, taskcount0/running1. Combining queued disable and preexisting exit flag yields bitsC00000 without executing a task or proving the real consumer ordering. Deinit does not wait for its queued control to complete. No live DMA/callback concurrency, production writes, flash, commits or index edits.

All prior967 seals,110 inputs and four checkpoints preserved. Next actual source leads: execute file-close lifetime and encoder setup, trace deinit callers relative to manager stop, and consume control through remaining hardware providers. Runtime producer quiescence remains separate from owner unregistration, recording state and early acknowledgment.
