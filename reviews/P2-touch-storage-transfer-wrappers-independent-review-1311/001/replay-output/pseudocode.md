# Touch storage transfer and erase wrappers

3520..355C and 3568..35A4 are each 60 instruction bytes with separate following literal pools. Both reject null buffer or unsigned modular u32(offset+length) greater than 256 with status four. The modular test permits overflowing sums; no stronger range check is inferred. Then read readiness byte; zero returns one. Otherwise pass incoming offset, buffer and length plus literal context in R3 to 8A78 (read) or 8AAC (write). Deeper status zero or accepted-status literal converts to zero; other statuses convert to two for read and three for write.

35B0..35D6 is a 38-byte erase wrapper excluding adjacent NOP/pool. Check the same readiness byte, return one if zero; otherwise call 8AE0(context). Convert deeper zero or accepted status to zero, others to three. All wrappers restore their two-word frames.

Receipt-derived original-instruction fixtures cover modular overflow, null/nonnull buffer, readiness and three deeper statuses. Deep helper boundaries are controlled without memory effects. Exact reached calls and arguments, return and SP are checked. Pointer validity, real storage and stronger logical bounds remain unresolved. No canonical admission or C implementation.
