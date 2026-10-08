# Protected bit thirty/thirty-one clear and set pair

Partial/unaccepted;134 instruction bytes480058..4800DE. BothroutinesPUSH R7,LR8;473940(live)fullresult→SP0 overwrites savedentryR7;finalMSR PRIMASKusesfreshSP0;POP R1,PC returns savedhelperresultinR1,notentryR7.

0058freshwordthrough480100&255 unsigned>=34→freshword480190clearbit21store,4807A0(1,live),ignoredreturn. Allpaths freshword4801F8clearbit31store;independentlyfreshsamewordclearbit30store;loadSP0MSR PRIMASK;4807A0(5,live),ignoredreturn;explicitreturn0.

009Efreshword4801F8setbit31store;independentlyfreshsamewordsetbit30store. Thenfreshword480100&255 unsigned>=34→4807A0(1,live),ignoredreturn,thenfreshword480190setbit21store. AllpathsloadSP0MSR PRIMASK;explicitreturn0. Preserveclear/set asymmetryofversioncheck/orderandfinalhelperonlyclearpath. No combiningRMWor timingmeaningofhelperarguments. Ownership/externalhelpers/MMIO/C/freeze/fullcoverageunresolved/notclaimed. Adjacent00DE..00E0zero2excluded.
