# PCM2.2 power updater and callback binding

Isolated alternative copies used by the215-object `aac9ab01bf1d628162a8ec528bf73bc2b04a1f655a88091795650e600b27ea45` successor. All three C objects compile byte-identically to the frozen candidate inputs using its recorded flags and `-I g2/components/bootloader/initializer_callbacks`. Do not link this dispatcher alongside the parent `startup_runtime.c`; both define the same entry points. Existing parent sources and build recipes are preserved.

The updater and most helpers were already reconstructed. This variant corrects signed-zero temperature classification, exposes fixed32-bit wrapper inputs, preserves previous PCM2.1 bindings, and installs native PCM2.2 boost handling. Source is locked-image-specific; callback table/storage addresses are fixed. Unsupported transition selectors and FPSCR side effects remain explicit limits. Read the owned `pcm22-power-integrated/REPORT.md` before extending claims or attempting a physical image build.
