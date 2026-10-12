# Native next provider contracts

Authenticated native EM source listing, base 0x302400, SHA256 0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03; ARC little-endian/dsp disassembly.

- 30da2c: fresh config count34 bounds then selected slot-active; error2; otherwise returns 32754c(id,value), whose native value is overwritten before use.
- 30e000: same count/active guards then returns 327694(id,first,second).
- 30da5c: count/active guards; if first==255 then second=0; first+second unsigned>255 or third unsigned>first yields18; third<fourth yields18; signed(first-second)<signed(third+fourth) yields18; else returns327630 with all six inputs.
- 30c65c: count/active guard2; native kind-valid31b768(third) failure17; paired slot words307044 highwordbit1 clear returns17; allocation6 null returns7; message half2=0x2801; freshhandler; byte5=third byte4=second half0=id; sendignored return0.
- 31b768: kind1 true; kind2 featurebyte805a95 bit0; kinds3/4 bit3; other0.
- 306fa8: native MPYUW(id,912); if kind4 substitute3; subtract boolean(kind!=3 OR originalkind!=4), slotbyte332+result; byte0x7e becomes0; signedextend result.
- 30bd34: critical enter before config reads; count/active error2; kind-valid failure17; successful bounds31026c(&local,secondout), query306fa8(id,kind), clamp310230(query), store firstout lowbyte; always critical exit, return status0/2/17.

These contracts guide subsequent source selection. No bodies or target completion are claimed by this note.
