# G2 FreeType TrueType community source

SPDX-License-Identifier: FTL

This component promotes the authenticated FreeType 2.9.1 TrueType closure from
research into the G2 community-source build path.  The unmodified implementation
comes from `third_party/freetype`; the small public property adapter in this
directory is also distributed under the FreeType Project License.

The authenticated closure accounts for 248 functions and 38,828 stock code
bytes: 13 driver-class callbacks, 74 direct private helpers, and 161 indirect
interpreter functions.  Both direct and indirect dispatch frontiers are empty.
The Cortex-M55 software link qualification includes the upstream TrueType module
and this production-path adapter and has zero unresolved symbols.

`FT_DEBUG_HOOK_TRUETYPE` deliberately remains null.  No setter is exported, so
`TT_Run_Context` uses the authenticated `TT_RunIns` fallback.  A future debug
provider must pass a separate typed source-admission review.

This is a community-source admission, not a stock-image patch admission.  The
shipping overlay remains unchanged until an IAR-compatible code-generation and
link-placement recipe is pinned and every relocated body passes the overlay's
byte-exact or reviewed-relocation gates.  External G2 font-payload identity and
stack/WCET qualification also remain release gates.

Run the controlled software-only gate with:

```sh
cd g2
make freetype-truetype-source-closure
```
