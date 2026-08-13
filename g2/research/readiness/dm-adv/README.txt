OpenCFW G2 Cordio dm_adv.c bounded readiness probe

Outcome
-------
* Local authenticated closure bounds nine linked stock functions / 562 code bytes in [0x004B3098,0x004B32CA), followed by a ten-byte literal pool.
* Six upstream APIs are source-only/dead-stripped: RemoveAdvSet, ClearAdvSets, SetRandAddr, SetChannelMap, SetAdValue, and SetName.
* Stock DmAdvSetData allocates sizeof(dmAdvApiSetData_t)+len and copies into pMsg->pData at message offset +8.
* That producer ABI exactly selects the Apache-licensed AmbiqSuite R2.4.2/R2.5.1 source/header fork; Packetcraft r19.02 and r20.05-c store an external pointer and do not match this function.
* The other fourteen definition spans are byte-identical between Ambiq and Packetcraft r20.05c.
* Os and O1 compile with DM_NUM_ADV_SETS=2 and stock-effective WSF assertions/traces disabled. Eleven external providers are enumerated; both isolated closure links have zero undefined symbols.
* This is a readiness/provenance build, not an IAR exact-byte comparison or production promotion.

Packaging
---------
Contains identities, hashes, stock ledgers, timings, and independently authored shims only. Excludes firmware, upstream source, decompilation, objects, ELFs, and caches. Stock range ends are exclusive.
