
undefined1
findConnIdByAddr(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  do {
    if (2 < iVar3) {
      return 0;
    }
    iVar4 = DAT_004d9110 + iVar3 * 0x30;
    if (*(char *)(iVar4 + 4) != '\0') {
      puVar1 = (undefined1 *)DmConnPeerAddr(*(undefined1 *)(iVar4 + 4));
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004d9120,DAT_004d911c,DAT_004d9118,0x1e,DAT_004d9114,puVar1[5],puVar1[4],
                     puVar1[3],puVar1[2],puVar1[1],*puVar1,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x11800000,DAT_004d9124,DAT_004d9124,puVar1[5],puVar1[4],puVar1[3],
                            puVar1[2],puVar1[1],*puVar1);
      }
      if ((puVar1 != (undefined1 *)0x0) && (iVar2 = FUN_004d294a(puVar1,param_1), iVar2 != 0)) {
        return *(undefined1 *)(iVar4 + 4);
      }
    }
    iVar3 = iVar3 + 1;
  } while( true );
}

