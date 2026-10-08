# P2-19071 independent review

Status: partial, unaccepted. No source or gate changes.

Fresh isolated replay passed for 0x468F24–0x468F9E (122 bytes, 49 instructions). Candidate and fresh instruction/reference records match exactly against locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`.

Checked the 24-byte saved-register frame and the FULL selector-two gate, fresh distinct diagnostic mask reads, and all stack-slot overwrites. The literal at 0x468F7C is loaded as a pointer then dereferenced for the word value; the separate literal at 0x468F7E is independently dereferenced for the later stored word. The 0x45A568 full result is compared to 1, and the success calls use the shown live arguments with R4 replaced by the literal address. Return from the final call remains outside this chunk. No child memory-fill or lookup contract is inferred.
