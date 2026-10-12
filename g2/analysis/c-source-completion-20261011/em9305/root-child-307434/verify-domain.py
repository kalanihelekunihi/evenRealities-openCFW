#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4]
b=(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes()
assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
t=b[0x334479-0x302400:0x334479-0x302400+15];assert t==(P/'sdk-switch.bin').read_bytes()
# Unsigned subtraction + CMP/JHI rejects all indices outside 0..14.
# EXTB and SEXB both preserve this domain; the 0x7ccf bit test narrows it.
accepted=[i for i in range(15) if (0x7ccf>>i)&1]
assert accepted==[0,1,2,3,6,7,10,11,12,13,14]
for event in range(65536):
 index=(event-21)&0xffffffff
 if index<=14 and ((0x7ccf>>index)&1):assert 0<=index<15 and index<128
for state in range(256):
 for index in accepted:
  target=t[index]
  for pending in [0,0xffffffff]+[1<<bit for bit in range(32)]:
   native=state==target or bool(pending&(1<<target))
   sdk=state==target or bool((pending>>target)&1)
   assert native==sdk
r={'status':'PASS_NATIVE_DOMAIN_AND_TERMINAL_PREDICATE_EQUIVALENCE','event_cases':65536,'accepted_indices':accepted,'table_bytes':15,'table_exact_sdk_stock':True,'limits':['Instruction-level native bound is unsigned 32-bit; finite event sweep is supplementary. Pending predicate equivalence follows bit-test/shift identity. Record-index bounds and final placement remain open.']}
(P/'domain-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
