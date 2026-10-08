# Runtime flag both bits two-three and single bit leaves

Partial/unaccepted;46instructionbytes,three separateleafentries. D8CE loadpointerliteral47D900;freshunsignedbyte[ptr];AND12;exact12returns1else0;UXTBthenBXLR. Thus47D8CEreturnsfull0or1 fromonefreshflagread,bothbits2and3set. No helpers/frame. This narrows mapped old/newresult ranges but preserves independentobservations across calls.
D8E4 separateentry:loadsamepointer;onefreshunsignedbyte;extractbit4;UXTB;BXLR. D8F0 separateentry:samepointer;onefreshunsignedbyte;extractbit5;UXTB;BXLR. Full0or1each. R1/R2/R3untouchedforallthree;R0returned,flagschangedbydecodedoperations. Distinctentryboundaries,no fallthroughbetweenleaves. Runtimepointer20075043establishedbypriorliteralreceipt,contentsnotfixedbyflash. No C/freeze/completenessclaim.
