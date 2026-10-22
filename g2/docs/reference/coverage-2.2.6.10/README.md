# G2 2.2.6.10 inventory coverage maps

Recovered 2026-10-21 during the source-reconstruction waves. Every row of
`g2/symbols/*.tsv` that is not implemented in `g2/src` (by name, `_<addr>`
suffix or a `/* Stock 0x... */` anchor) is classified here:

- `upstream-map.tsv` — rows identical to (or an out-of-line inline copy from) a
  pinned upstream source; the C is compiled from `third-party/upstream`, not
  rewritten. Several files still need a `sources.json` unit (see follow-ups).
- `data-map.tsv` — rows that are literal pools, rodata, or labels inside
  another function (inventory artefacts).
- `blocked-map.tsv` — rows identified as licence-restricted vendor libraries
  (Nordic nrf_fuel_gauge, NemaGFX/NemaVG, EM9305 SDK / Packetcraft controller,
  Cypress CAPSENSE / Em_EEPROM). Identified only; not reconstructed pending the
  repository owner's decision.

Compilation is not byte identity; nothing here is a byte-identity claim.
`followups.md` lists the integration, deduplication, naming and inventory
corrections found during the waves.
