# P2-20965 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay: PASS in isolated output (`analysis/review-isolated-P2-20965/fresh`); output data exactly matches candidate. Locked input SHA-256 is `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

The extraction is 32 bytes at 0x47E614..0x47E634: eight aligned little-endian words, with 11 recorded PC-relative load consumers. Every word start is represented; independently checked the displayed aligned-PC literal targets against the consumer records. No pointer ownership/exhaustiveness claim.
