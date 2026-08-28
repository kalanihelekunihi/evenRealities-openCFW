<!-- SPDX-License-Identifier: MIT -->
# G2 touch CAPSENSE provider boundary

After completing the CAT2 PDL census, the largest remaining coherent block was
the 55-function interval previously labeled `capsense_cat2_mixed`. The closed
CAT2 census and call topology now resolve this ambiguity: these entries form a
CAPSENSE middleware boundary, not additional open CAT2 admissions.

The graph contains one 50-function component, one two-function component, and
three ingress-isolated leaf functions. Its external edges terminate in already
classified application, MSCLP/PDL, runtime, delay, and touch-policy providers.
Every shipped body retains an authenticated instruction hash and explicit
internal/external edge list in the manifest.

The official Infineon `capsense` release `release-v3.0.1` at commit
`25fa1cd5abb4cc66981b04f8872d57d74e398976` is pinned as a comparison and
provider-API reference because it is the first public fifth-generation release.
It is not asserted to be the exact historical revision used in the glasses.
The release version, EULA hash, `version.xml` hash, source count, and source
inventory digest are pinned so a future audit can reproduce that comparison.

The vendor license permits specific firmware use but is not an open-source
license and restricts source redistribution. Consequently, none of these 55
bodies is copied, adapted, or counted as concrete OpenCFW source. Each is typed
`typed_external_eula_provider_boundary` and marked for clean-room
reimplementation or an explicitly supplied provider.

The new MIT boundary exposes only coarse initialize, scan, process, calibrate,
and interrupt operations. It contains no vendor implementation semantics,
performs no host MMIO, is not production-routed, and returns a fail-closed error
without an injected provider.

This closes the 55-row mixed-provider attribution gap while reducing the
remaining actionable semantic/source census from 166 to 111. The 55 typed
external rows remain non-source and must not be represented as open firmware
completion.
