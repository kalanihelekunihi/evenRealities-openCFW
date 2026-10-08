# P2-19107 independent data review

Status: partial, unaccepted. No source or gate changes.

Locked image SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. Fresh extraction verifies 0x469576–0x469580 as `00 00 4F 4E 00 00 4F 46 46 00` (alignment zeros plus ON and OFF strings with terminators). This fills the precise gap following the handler return and before the next entry; it does not infer string semantics beyond the observed bytes.
