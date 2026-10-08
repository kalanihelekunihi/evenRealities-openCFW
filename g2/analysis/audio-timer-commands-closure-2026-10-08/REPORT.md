# Timer stop/delete: queued ownership versus daemon completion

**32 PASS original/independent daemon comparisons**. Real generic command producer0x47E7B0, queue initializer/send/receive, list-remove, fixed-time helper and heap-free peers execute. Independent C reconstructs selected stop/delete consumer logic; it shares original queue/list/heap/time peers, not an entire independent kernel. [Source](../../components/audio/timer_commands_offline/timer.c), [ARM32 layout](../../components/audio/timer_commands_offline/timer.h), [results](results.json).

## Publication does not perform stop or delete

Generic command producer sends a sixteen-byte message to queue from0x20074AB0: signed command+0,command value+4,timer pointer+8,union padding+12. Tests execute producer with command3(stop) or5(delete), zero value/block timeout and coherent real initialized queue. It returns enqueue success while **all44 timer bytes and timer-list bytes remain unchanged**. Producer and consumer are then invoked sequentially by the test; no live daemon scheduling is claimed.

Original command drain0x47E97A repeatedly receives with zero timeout. For nonnegative commands, it first unlinks timer state item if container!=NULL, samples tick/overflow, then acts. Selected command3 clears active bit. Command5 frees the timer object if dynamically allocated; for static object it retains storage and clears active bit. The previous queue-deletion batch is a separate object/path: it must not be substituted for timer-command completion.

## Layout and lifecycle table

Timer prefix44 bytes: name pointer+0,list item+4 (value/next/previous/owner/container), period+0x18,ID+0x1C,callback+0x20,opaque word+0x24,status byte+0x28. Status bit0 active,bit1 static,bit2 autoreload. Opaque word meaning is deliberately not assigned here. ARM32 message16 bytes and timer prefix44 are compile-time checked in header.

| Step | Proven selected ownership effect |
| --- | --- |
| Producer enqueues3/5 | Queue copies command and borrowed timer pointer. Timer/list unchanged. No pointed-object release. |
| Daemon receives | Message copied to daemon stack; queue count decreases. Timer must remain valid for dispatch. |
| Daemon unlinks timer | Original list-remove clears item.container and adjusts list/sentinel/count. |
| Stop3 | Active bit clears; allocated timer retained. |
| Delete5 static | Active bit clears; static timer storage retained. |
| Delete5 dynamic | Actual heap free reclaims synthetic56-byte allocation (44-byte object plus8-byte header/alignment). No timer callback/destructor runs in this selected path. |

Four sequences(empty,stop,delete,stop+delete), static/dynamic, linked/unlinked, autoreload0/1. Dynamic fixture is a coherent56-byte block with allocated bit; static flag shares same storage fixture solely to demonstrate no free. Timers linked initially have active bit set; unlinked timers inactive. Direct generic stop command to an inactive timer is not proof that CMSIS stop accepts it: actual wrapper0x4494D8 checks active and returns resource error when inactive.

Time is held at100, matching last-sampled time at0x20074AB8; no tick wrap, expiration, callback or timer restart executes. Empty task waitlists, taskcount0/running1; synthetic scheduler state excludes wake/yield. Queue copies and object state/list/heap bytes compare. Trace rejects wrap/tick/yield providers. Full dynamic allocation/booted timer creation and CMSIS auxiliary callback memory are not modeled.

## Remaining ownership dependency

Actual CMSIS timer delete0x44953E statically reads timer ID via0x47EB26, enqueues delete5, then may free an auxiliary callback block when ID bit0 is set. That auxiliary allocation path is **not tested here**; neither this selected daemon free nor enqueue success proves its callback lifetime safe. Timer callbacks already executing, commands pending behind others and actual daemon priority/order require further analysis/runtime evidence.

Audio's event8 acknowledgment still precedes cleanup. Timer-stop/delete enqueue success, queue free and producer quiescence remain different milestones; this batch demonstrates deferred timer-object release without asserting hardware safety. Build_offline.py then opencfw venv verify.py. Prior967 seals/110 inputs/four checkpoints preserved; no commits,index,production/device writes. Next source leads: CMSIS auxiliary callback ownership, real timer callback cancellation/expiry, and complete timer-daemon scheduling. Source is not exhausted.
