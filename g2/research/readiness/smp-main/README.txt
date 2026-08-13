OpenCFW Cordio smp_main.c Lorelei readiness handoff

Outcome
-------
* Packetcraft r20.05c smp_main.c is authenticated at commit 3656312d..., tree 0a76c7dd..., blob ba488930..., SHA-256 c0d63cc6....
* The isolated Ambiq AES stale-token queue cleanup patch is authenticated by base, patch, and result hashes. The patched result adds WsfMsgDeq and secCb provider dependencies and increases SmpHandler from 104 to 136 bytes under Os and from 124 to 164 bytes under O1.
* Base and hybrid Os/O1 objects compile successfully. Base objects expose 30 providers; hybrid objects expose 32.
* Hybrid closure links are valid and retain 1,969/2,159 text bytes plus 260 BSS bytes with zero undefined symbols.
* The base closure ELFs retain zero text/data/BSS. Their zero-undefined files are therefore vacuous and must not be cited as proof of provider closure; the original smp_main.o undefined ledgers remain the authoritative base provider inventory.

Scope and limitations
---------------------
The hybrid includes public r20.05c sec_main.h and the available win32 wsf_os_int.h solely to establish structural build readiness. This does not prove the stock RTOS ABI or an exact firmware match. The pending scratch did not retain complete compiler command lines, so this handoff authenticates the toolchain, dependency closure, object/result hashes, attributes, and timings without claiming byte-for-byte rebuild reproducibility.

Packaging
---------
This archive contains compact ledgers, hashes, timings, README, and the independently authored assembly closure shim. It excludes Packetcraft/Ambiq/hybrid source, the patch body, firmware, decompilation, objects, ELFs, and caches.
