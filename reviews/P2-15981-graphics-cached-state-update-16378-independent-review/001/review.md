# Independent review 15981

Partial, accepted:false. Fresh decode replay passed for 112 bytes. Uses a default object only when entry R0 is null, reads stacked force byte and signed fifth byte, then performs ordered short-circuit cache comparisons with signed byte interpretation. Cache hit returns the final signed fifth byte in R0. Update path calls 513924 then publishes word +80 and bytes +84/+85/+86 regardless of child result.

Child/global/hardware effects remain unqualified; no admission or gate change.
