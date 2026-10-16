# Same-pin musl memmove subset

Unchanged src/string/memmove.c from musl v1.2.5, commit
0784374d561435f7c787a555aeab8ede699ed298, retrieved from the primary upstream.
The accompanying COPYRIGHT retains the upstream MIT license. Provenance binds
both files. This source candidate adds overlap-safe movement without changing
the existing memory runtime pin or receipts. Future improvements require an
explicit new pin and rerunning overlap and native consumer contracts; no original
firmware dependency version or instruction identity is claimed.
