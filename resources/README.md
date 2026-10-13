# Byte-exact firmware resource catalog

Local vendor-derived resource inputs live under `g2/s200-v2.2.6.10/`. `manifest.json` records 1,191 typed non-executable resource structures and exact source hashes/ranges; `blobs/` holds verbatim original bytes. `verification.json` confirms each record reconstructs exactly. No firmware source or reference target changed. These retained bytes are analysis/build-placement inputs, **not** completion of the required byte-identical build from reconstructed source.

The catalog distinguishes three separate claims:

- **Resource identity:** stored records have validated original structures/extent/hash; font roots additionally bind original callbacks and ABI. This is not a file format portability claim.
- **Consumer relationship:** font chains and opacity table have static original-consumer evidence. Other records preserve prior receipt evidence; pointer candidates alone do not prove a consumer.
- **Necessity:** `necessityStatus` explicitly identifies bound-font dependencies versus unresolved UI/product necessity. All 428 images and all embedded strings must not be called essential merely because they exist. `reviewGroups` indexes the two necessity review sets. Suspected string/path candidates and mixed/executable regions remain outside the blob catalog, linked in the detailed analysis evidence.

Files are content-addressed union segments, not falsely named portable `.ttf`, `.png` or standalone configuration files. Every record's `sharedSlice` gives its exact offset/length inside a blob. Overlapping/touching source intervals share one union blob, and identical content across source domains can share a blob. Source-domain unions: **785,326 bundle-bound payload bytes** and **180 decoded initialized RAM bytes**. Physical stored bytes: **785,113**, in **375** unique blobs and **411** source-domain segments. Decoded RAM never adds to the flash denominator. Source records retain original component SHA-256, bundle translations, loaded-address mappings, lengths, type/encoding, descriptions, dependency pointers, consumer evidence and confidence. The bundle SHA-256 remains `f4dfb0b49ad3de3c2daf17f8a27a157c3dc98411d6a0d3ab2cfd0918f41b9afa`.

## Reproduction and safe future extraction

From repository root:

```
python3 resources/build_g2_catalog.py
python3 resources/extract.py
python3 resources/extract.py --verify
python3 resources/test_extract.py
```

Catalog construction consumes the current validated local resource dataset, authenticates each input, and writes metadata. Extraction authenticates the target bundle and every source, then creates absent blob files exclusively. Existing correct files are reused; conflicting files cause failure and are never overwritten. Verify-only checks every byte/hash without replacing blobs. The script never executes payloads, mounts storage, flashes devices, rewrites pointers or mutates sources. New discoveries require new explicit authenticated extents and evidence in a reviewed catalog; there is no heuristic extraction fallback or executable payload runner.

`blobs/*.bin` are present locally and untracked alongside the manifest, scripts and documentation; no files have been staged or committed. No ignore rules were changed. User-requested repo-local inclusion does not itself publish files to GitHub. Do not push proprietary bytes while publication authorization/rights are unresolved.

## Build placement and dependencies

Font descriptors contain absolute little-endian 32-bit addresses into the original image. Keep their font root, glyph descriptors, cmaps, Unicode/offset lists, bitmap stores and opacity palette together at original placements. A font-root RAM record must be reproduced in the corresponding initialized RAM transform at its original loaded address; it cannot be dropped into flash at an invented offset. L8 descriptors similarly refer to raw grayscale pixels by absolute address and include original size/stride. Image/font preview PNGs and PGMs remain separately in the linked `resource-expansion/` evidence folder; they are inspection artifacts, never byte-identical firmware replacements.

Tables, model weights, configuration records, vectors, embedded strings and metadata retain their original domains and relocation relationships. Consumer references for many remain unresolved; the manifest preserves that limit. Outer bundle header/TOC/CRCs belong to the packaging workflow, not guessed flash addresses. A linker or generator must preserve layout/ABI and reproduce exact pointers; raw assets alone do not establish complete functional firmware or exact rebuild acceptance. No external NOR files are included: authenticated contents and valid LittleFS/FlashDB geometry/state are unavailable. The catalog excludes seven compressed mixed initializers and four whole initialized RAM copies; only the five typed decoded font roots (180 bytes) are extracted from the decoded domain.

## Rights and provenance

Official Even Realities firmware, fonts, images and other extracted vendor data retain their original rights. **Root MIT does not license these bytes. Redistribution permission is not established.** See root `NOTICE` and the manifest's per-source provenance. Source font names/artwork authorship are unknown; static Unicode mappings and recognizable shapes do not identify a license. Original project-authored extraction tools and documentation are separate from proprietary inputs. No Library upload or external publication occurred; the prior owner-approval blocker remains pending.
