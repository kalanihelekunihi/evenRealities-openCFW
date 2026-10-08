# Kernel-state lifecycle retake — 4598

Pinned ELF SHA-256: `4598040563d8f41b2fc71d430114b6b8564198b439e7225e9729d2f1c93acc2e`. The `verify_kernel_state_candidate.py` run passes 216 cases / 224 distinct original instruction bytes. Result receipt SHA-256: `cb42a7b9048080844e9f9468adc27f94de162969869774ecbcddb61641d98e09`.

This candidate includes the native kernel-state binding. The suite directly executes stock `0x416088` and source `opencfw_boot_kernel_state` with equivalent no-argument, uint32-return ABI. It injects identical synthetic kernel-start returns on each side and initializes IPSR/PRIMASK/BASEPRI/state RAM. It does not claim actual scheduling, interrupts, or physical hardware behavior. Earlier DCE and 408 receipts remain unchanged.
