# Stored callback-root integration — pending independent audit

Discovery's fresh static data result narrows the earlier callback gap: stored slot10026D38 contains20026D3C; authenticated32-byte descriptor binds sample-app init10208E4C,event10208F04,loop102091BC,suspend10208DEC and resume10208DCC, plus name/private string fields. Descriptor identity is available; it must no longer be described as unavailable solely because earlier receipts lacked target pointers. This is pending independent audit and does not authenticate a unique sample-app producing source.

Existing in-image entry/system_init/main calls supply static startup→app initialize→event tick chain. Guarded indirect calls consume descriptor fields. Clear-BSS bounds begin20026D80, above the root; root is stored initialized data, not newly proved runtime assignment or immutable state. Exact literal scans cannot exclude computed stores.

Runtime visibility remains unproved. Normal loader arguments copy14716bytes to IRAM10023400–10026D7C, containing root/descriptor. Linker expects initialized data in DRAM2002xxxx; no direct helper write/translation to20026D38 is established. Numeric offset and paired linker intent are corroboration, not physical alias proof. Preserve loader start-data200264E4 versus aligned section boundary100264E8 four-byte distinction.

Required next input: authenticated normal-path address-space/translation contract, or instruction-backed helper/DMA write contract proving exact DRAM visibility. Then entry reachability/callback outcomes remain separate. Static vendor documentation could close visibility; no hardware writes or execution are required or authorized here. Avoid duplicate root scans or claiming external startup blocks available in-image evidence.

Case FLASH comparison remains separate: official headers confirm corrected ordinary/option labels, but the single compiled comparator differs in28-byte code and does not identify the producer. No canonical, historical symbol, production, Git or device changes.
