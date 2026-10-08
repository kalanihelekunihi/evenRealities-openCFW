# Runtime maximum-raw boundary and integer correction

New independent offline source/header: ../../components/touch/max_raw_offline/. Locked identities, reset fields, pinned SDK comparator hashes and original addresses are in provenance.json; original-disassembly.txt records the call chain and arithmetic.

Initialization at0x7278 visits enabled widgets0..2 and calls0x5cac, OR-ing statuses. Wrapper5cac checks widget-contextstatusbit8 (max-count calculation requested), calls saturated scan7bc0(output,id,firstSlot,u32mode0,context), clamps output to65535 and writes contextu16+4. It does not clear the request flag, and writes the returned value even on nonzero scan status. No request leaves existing maxRaw unchanged and returnszero. Startup maxRaw0 is NOT evidence that it remainszero after initialization, nor a basis to assume the synthetic3000 used in tests.

Saturatedscan7bc0 obtains HW pointer from *(*commonConfig+8), switches hardware state through6ac0(mode5), and builds a temporary scan frame from context+40 slot stride28 (type7 uses context+44 alternate frame). It masks the temporary control word, loads frame6928, computes watchdog7288, and waits through6980. A zero wait result ORs status4 (timeout). Even after state-switch failure or timeout, the actual body reads FIFO at HW+0x3200 low16 and clears HWCTL bit31, then applies arithmetic and returnsstatus. Thus nonzero status must be honored; output is still populated. These scan helpers/hardware transitions have not been reconstructed/tested in this batch.

Recovered postprocessing7c4e..7c9a:

`divider=(scan_control>>16)&0xfff; kref=divider+1; epi=(clockSourceLow2==2?96:2)*((divider+4)>>2);`

Subtract one from epi for evenkref, or for source2 with senseMethod1/10. Then compute unsigned32 `(fifo-epi)*chopCycles`; if result>=65536 choose65535, else retain result; replacezero withone. Unsigned underflow is preserved, not clamped before multiplication. Consequently too-small rawFIFO can produce65535; it is not a validated physical measurement in that situation. Pinned Infineon6.10 LP source independently explains this as epilogue correction, PRS clock selection and chop-cycle scaling. No uniquely identifying upstream version/byte equivalence is claimed.

Validation:1440 register-seeded original-instruction arithmetic slice comparisons versus nativeC across FIFO0..65535, dividers0..4095, allclocklow2 values, methods0/1/10 and chop0/1/2/255.60 wrapper comparisons execute original5cac versus native adapter with EXPLICIT saturated-scan stub on both sides, varying scanvalue0..FFFFFFFF, status0/4/8 and request flags. Stubbed wrapper tests do not prove scan/MMIO behavior. Arithmetic slice has no function-call stubs; registers/stack are synthetic.

Remaining boundary: actual FIFO values and state/scan helper success depend on MSCLP acquisition. Available OTA bytes allow further static software reconstruction of6ac0/6928 and inline saturated-frame construction; analog response, board excitation/calibration and physical acquisition timing need hardware traces or a validated peripheral model. No claims of source-complete firmware, hardware acquisition or safe patch follow from these tests.
