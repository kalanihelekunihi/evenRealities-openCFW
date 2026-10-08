# P2-20945 independent review

Status: **partial / unaccepted**.

Fresh replay passed against the locked image (SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`). The three disjoint 4-byte ranges total 12 bytes and match exactly: 0x47E084=`74 70 5F 00`, 0x47E140=`72 62 00 00`, and 0x47E174=`77 62 00 00`. Candidate and fresh `data.json` hashes match (`f268f1a6efabb15ed7a2e21e965c1ff8f9a8172503c8f4f508fc8c7a5381330d`). All four mapped ADR consumers were found in receipt-verified component maps; independently calculated aligned-PC targets resolve to the recorded three ranges.

The bytes can be described as `tp_`, `rb`, and `wb` followed by zero bytes. This does not establish API meaning, ownership, exhaustive consumers, or classification of intervening bytes. Candidate stays partial/unaccepted; no source or gate files changed.
