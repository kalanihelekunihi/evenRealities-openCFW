# Timer-service restricted queue wait in C

The selected native-layout queue implementation now includes pinned FreeRTOS
10.5.1 `vQueueWaitForMessageRestricted`. Stock entry 0x95f8e is 68 bytes:
lock the queue, place the timer task on its receive event list if empty, then
unlock. REA confirms the entry, full instruction range, calls, and terminal
branch to the existing queue-unlock routine at 0x85534.

[Machine-readable evidence](queue-restricted-c-dependency-review.json) binds the
stock REA instructions, upstream selection, C source, differential probe,
negative controls, audit, full build and hybrid report by SHA-256.

The actual stock and C wait/lock/unlock routines agree in 6,400 paired cases
(12,800 executions). Cases combine receive/transmit lock bytes -128, -1, 0, 1
and 127; empty/nonempty queues; zero/two waiting tasks; missed-yield results;
four entry interrupt masks; and boundary tick/indefinite-wait words. Restricted
placement receives the exact event-list pointer and original argument words.
The fixture can synchronously inject an arrival during the locked wait, testing
subsequent unblocking and missed-yield dispatch. Complete queue snapshots and
call ordering, final SP, callee-saved registers and interrupt masks agree.
Omitting the initial lock or ignoring message count is detected.

Critical boundaries and scheduler placement/remove/missed-yield operations are
modeled. This is not asynchronous IRQ or scheduler integration proof. Valid
queue storage and an already suspended scheduler are preconditions; malformed
pointers, private frame identity, caller-clobbered words/flags and physical
concurrency are outside the comparison.

All 27 preexisting queue-unit function bodies remain byte unchanged. All 573
R1 units compile without failures or duplicate strong symbols. The application
import set loses only `vQueueWaitForMessageRestricted`, falling from 184 to 183;
bootloader imports remain 34. Five qualification profiles select only two
already covered BASEPRI regions; the new wait body is not byte-qualified.
The source plan remains unchanged at 3,833 source-built bytes, 642,327 retained
executable bytes and 248 resource bytes. The hybrid still equals the locked
application byte for byte; complete source linking and hardware operation remain
unproven. No G2 corpus gate advances.

The hardware dependency review also distinguishes the public demo's unresolved
`gh3026_*` reset/IRQ hooks from the stock registry-backed Goodix reset/IRQ
routines already in `goodix/stock_i2c_transport.c`. Their demo names alone do
not establish a stock binding. Those imports remain pending call-site evidence;
no GPIO polarity, pulse timing or wrapper semantics are guessed to close them.
