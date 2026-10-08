# P2-21059 independent review

Status: partial / unaccepted. No source or gate changes.

Fresh replay passed for 0x47F90C..0x47F942 (54 bytes); instruction/reference outputs match candidate. The full-pointer null path returns 6 without store/call. Nonnull path first writes byte zero through the output pointer, then calls EF18 with LOW8 index and the local record buffer. Full nonzero result returns unchanged, but the initial zero is not guaranteed to remain if output aliases memory modified by the call. On helper-zero path, separate SP8/SP12 reads determine an output byte 0/1 and the function returns explicit zero. Teardown discards the 16-byte record before popping the remaining frame. Aliasing and store order are retained; no ownership claim.
