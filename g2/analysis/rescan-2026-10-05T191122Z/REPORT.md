# OpenCFW rescan — 2026-10-05 19:11 UTC

Compared with the 18:04 UTC scan: 22 foundation C/header files versus 15, comprising nine implementation C files, ten interface/compatibility headers and three simulator entry/seam C files. Seven files were added: GPIO IRQ implementation and two headers, CMDQ implementation/header, interrupt-mask implementation/header. The lifecycle simulator seam also changed.

All 22 source hashes, five callable ELF hashes and five saved evidence hashes match the independently reviewed GPIO cumulative inventory. No foundation source is ignored. Git initially showed 230 staged paths, zero unstaged paths and zero untracked paths; this scan did not stage anything. Root .gitignore line 15 (`build/`) hides compiled simulator output; *.elf and *.o rules also apply. No configured global excludes were found. This does not hide the new C/header implementation.

Fresh `make -C g2 foundation-test` passed all 33 tests (11 touch, 15 Ambiq, seven resource preservation). Native emulation was not rerun: saved, hash-authenticated evidence includes 773 GPIO comparisons and 435 real-critical/CMDQ comparisons. Cumulative executed-original evidence is 1,392 unique bytes after removing shared helper overlap; six statically unreachable GPIO bytes and the inconclusive scatter decoder are excluded. The saved aggregate has 183 passing methods, zero failures/errors, six method skips and one class setup skip; it was not rerun for this scan.

Protected firmware, manifest, workflow state and open_cfw.py hashes remain unchanged. There are still zero fully blob-free production payloads and no proven source-built byte-identical bundle. These callable foundation modules demonstrate bounded behavior, not a complete bootable firmware. Physical radio interrupt delivery, asynchronous callback publication safety and clock/delay timing remain unverified.

Next useful vertical analysis is the pin117 radio registration/enable/dispatch/teardown chain. GPIO registration writes handler then argument without its own critical section; its race safety cannot be established by the existing serialized synthetic tests.

See comparison.json for exact paths, hashes and delta, and ../ambiq-gpio-irq-2026-10-05/REPORT.md for GPIO behavior and limits.
