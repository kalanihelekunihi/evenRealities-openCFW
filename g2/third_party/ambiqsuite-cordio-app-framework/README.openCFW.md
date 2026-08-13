# AmbiqSuite Cordio application-framework oracle

This directory admits the nine Apache-2.0 Cordio application-framework files
from the public AmbiqSuite 2.5.1 import at commit
de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f. They explain the ancestry of all
nine retained stock paths under the Cordio apps/app source directory.

This is not a pristine G2 checkout. The stock firmware preserves Ambiq's
application framework, including the three-argument role-aware AppDbNewRecord,
NVM hooks, extended connection state, legacy advertising state initialization,
and Packetcraft handler/discovery architecture. G2 then adds a much larger
ten-record MRAM database plus product-specific connection, privacy, pairing,
discovery, diagnostics, and UI behavior. The selected source is therefore a
rebuild oracle and semantic shortcut, not an exact text or compiler-output
claim.

Four files (app_disc.c, app_master_leg.c, app_server.c, and common/app_ui.c)
are blob-identical in the authenticated AmbiqSuite 2.3.2, 2.4.2, and 2.5.1
imports. Five changed at 2.5.1; stock's role-aware database, extended
connection, and legacy-advertising behavior select the 2.5.1 family as the best
available baseline. The historical private G2 producing commit remains
unobservable.

Run python3 verify_snapshot.py for offline source authentication and
`make cordio-app-framework-lineage` for the authenticated stock lineage audit.
No file in this directory is production-routed.
