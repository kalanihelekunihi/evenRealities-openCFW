# Authentic DSP C compiler comparison

Verified execution: local authenticated archive supplies C-SKY Tools V3.10.15 Minilibc abiv2 B20190929 GCC 6.3.0. Existing amd64 Docker image opencfw/iar-base:10.10.2-local executes it offline with network disabled, read-only root, read-only tool/repository mounts and isolated analysis output. No new image, system security setting, compiler installation or firmware execution was needed. The earlier mount failure remains in compiler-host-verification.json.

All five unchanged authentic Apache-2.0 C units compile successfully with one DWARF-derived recipe: -mcpu=ck804ef -mhard-float -O2 -g -fno-builtin -fstrict-volatile-bitfields -ffunction-sections -fdata-sections. Header lookup was completed using SDK Makefile-declared include/utility/libdsp, include, arch/soc/grus/include and include/utility. Earlier missing csi_core.h and util.h attempts remain separate receipts. No feature-macro or optimization flag sweep occurred.

Complete selected sections differ: shift 368 versus stock116 bytes; copy84 versus44; fill70 versus40. Hashes also differ. Zero selected C sections reproduce stock under this recipe. No padding removal, relocation masking or byte normalization was performed. Compilation success is separate from equality, numerical correctness and final linking.

The transform C units compile wrappers (csky_cfft_radix4_q15 56 bytes, csky_rfft_q15 110 bytes), not definitions of the four selected butterfly/split kernels: those remain undefined references in these objects. No selected C abs-max or bitreversal counterpart was asserted. This checkout deliberately supplies selected kernels through assembly; a wrapper object is not source reproduction of its dependencies.

The independently checked seven assembly sources still reproduce nine selected sections totaling1606 bytes; 17 audit checks passed. Their sealed packet is unchanged (assembly-seal-check.json). This corrects the predecessor's historical compiler-availability boundary additively: the exact compiler archive was already local and is now executable.

The finite fixed-recipe C comparison is complete. To pursue exact C reproduction, obtain authentic kernel C definitions where absent and the producing per-file compiler/macro/configuration recipe or corresponding historical source revision. GCC version alone does not identify that recipe; mismatches do not prove semantic defects or unique original producer. Current licensed assembly already provides the stronger exact-byte rebuild path for these nine kernels. Numerical execution, private caller/GSC source, CPU alias visibility, startup selection and whole image linking remain separate unresolved work.

Structured evidence: toolchain.json; c-build-results.json; c-build-sdk-header-results.json; c-build-complete-header-results.json; comparison-summary.json; retained objects and replay scripts. No Git/production/canonical/Pigweed/device changes. No C-compilable percentage or canonical admission is claimed.
