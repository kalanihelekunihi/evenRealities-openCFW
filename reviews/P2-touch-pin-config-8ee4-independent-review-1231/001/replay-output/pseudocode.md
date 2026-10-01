# Touch pin configuration valid paths

The body8EE4..8F92 rejects null base or null configuration with005A0001. Nonnull paths contain BKPT1 checks for pin>7 and configuration fields beyond their bounds: u32+0<=1, u32+4<=15, byte+8<=15, u32+12<=3, u32+16<=1 andu32+20<=1. Breakpoint continuation is not modeled as input rejection.

Valid paths call8E64(base,pin,u32+0),8E84(base,pin,u32+4),8E28(base,pin,byte+8),8EBE(base,pin,u32+12). Each raw helper return is ignored. The last two fields are checked again after these calls. Fresh reads of base+8 update bit24 from field+16, store, then freshly read again and updatebit25 fromfield+20 andstore. Returnzero and restore16-byteframe. Helpermutation ofconfiguration orMMIO may affect these laterfreshloads.

Twenty-four original-instruction valid-path fixtures check both pin boundaries, both flags and three initialregisterpatterns. The four helpers are controlled to returnFFFFFFFF without memoryeffects, demonstrating ignoredstatus only under that contract. Null andbreakpoint paths are staticevidence, dynamicallyuntestedhere. Physicalregisterbehavior,breakpointsemantics andhelpercontracts remain unresolved. No canonical admission orCimplementation.
