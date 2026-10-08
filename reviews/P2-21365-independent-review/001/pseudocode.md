# Integer radix and pointer V suffix selection

Partial/unaccepted;126 instructionbytes483B60..483BDE,continuation88-byteframe483960. Pendingu equality→483B68;otherwisecompare120x,NE→483F98unresolved;EQ integerentry. Each subsequent conversion test independently rereadsSP48cursorbyte. x orX→R10radix16. p orP→radix16,R8|=16alternate,R8|=256long;freshcursorbyteat+1 compare86V;EQ freshcursor++storeSP48 (nowpointsV),NE unchanged;both483BCE. o→radix8;b→radix2;allotherintegerentry→radix10,R8&=~16alternate.

483BCE freshcursorbytecompare88X;EQ→483BDEunresolved. Otherwisefreshcursorbytecompare80P;NE→483BE2unresolved;EQfallthrough483BDE. Preserve V consumption before subsequentcase checks, repeatedfreshreads and exact flag changes. No C,freeze,wholecoverage or equalityclaim.
