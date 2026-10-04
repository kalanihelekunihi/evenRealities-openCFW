# P2-9035 independent scoped review

Status: PASS_SCOPED; accepted: false; status: partial.

- Fresh original-byte replay passed all 512 categories x two PRIMASK values using original default flash tables and no-op target stubs; high-category callback slot was null.
- The replay verified full packet preservation, return of saved entry R7, preserved registers, PRIMASK, SP, and stop PC.

Limitations:

- The registration calls are not executed; callback-present, concurrency, and physical behavior remain outside scope.
