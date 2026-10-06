# Queue reservation commit, 0x538FB4..0x53901A

Partial; accepted:false.102 original instruction bytes,leafnoframe/children. CachequeueR2entryR0;entryR1markerflag. NULL/badmasked01FFFFFFsignature!=01CDCDCDreturns2;word[q16]==word[q20]returns7. Validpendingpathordered:

node=freshword[q20]
marker=(u8(flag)!=0 ?1:0)|word[word[q36]+8] // indexaddress itself,not pointee
word[node]=marker
word[node+4]=freshword[q32]
word[q20]=u32(node+8)
word[q16]=freshword[q20]
if word[q8]>=20080000:DMB SY
value=freshbyte[q32] // not full producerword
publish_pointer=word[freshword[q36]+12]
word[publish_pointer]=value
return0

R2queue retained. Queueproducer32notincrementedhere;allocationalreadydidso. Markerappendedafterreserveddata, consumes8bytes. Pointerpublicationlast afterconditionalbarrier; fields/signature validatedonlyatentry. Outputaliases ormappingmutationcanalterfreshreads. Noenabledstatecheck,interruptmaskingorchainvalidation. PhysicalDMAvisibility,alignmentfaults/concurrencyunqualified. No C/admission/gates.
