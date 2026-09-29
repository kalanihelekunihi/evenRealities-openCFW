
undefined4 FUN_0047a8c4(char param_1,undefined1 *param_2)

{
  bool bVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  byte bVar6;
  
  iVar3 = DAT_0047ae64;
  bVar1 = false;
  if (param_2 == (undefined1 *)0x0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x3e6,DAT_0047b464);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0047b484);
    }
    uVar4 = 0;
  }
  else if ((param_1 == '\x01') && ((param_2[5] & 0xc0) == 0x40)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x3ee,DAT_0047b4b4,param_2[5],param_2[4]
                   ,param_2[3],param_2[2],param_2[1],*param_2);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x11800000,DAT_0047b4b8,DAT_0047b4b8,param_2[5],param_2[4],param_2[3],
                          param_2[2],param_2[1],*param_2);
    }
    for (bVar6 = 0; bVar6 < 10; bVar6 = bVar6 + 1) {
      if (((*(char *)(iVar3 + 0x2f) != '\0') && (*(char *)(iVar3 + 0x30) != '\0')) &&
         ((int)((uint)*(byte *)(iVar3 + 0x2e) << 0x1d) < 0)) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x3f8,DAT_0047b4bc,bVar6);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0047b4c0,DAT_0047b4c0,bVar6);
        }
        DmPrivResolveAddr(param_2,iVar3 + 7,bVar6);
        return 1;
      }
      iVar3 = iVar3 + 200;
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x404,DAT_0047b4c4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0047b568,DAT_0047b568);
    }
    uVar4 = 0;
  }
  else {
    cVar2 = DmHostAddrType(param_1);
    for (bVar6 = 0; bVar6 < 10; bVar6 = bVar6 + 1) {
      if ((((*(char *)(iVar3 + 0x2f) != '\0') && (*(char *)(iVar3 + 0x30) != '\0')) &&
          (*(char *)(iVar3 + 6) == cVar2)) && (iVar5 = FUN_004d294a(iVar3,param_2), iVar5 != 0)) {
        bVar1 = true;
        break;
      }
      iVar3 = iVar3 + 200;
    }
    if (bVar1) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x419,DAT_0047b56c);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047b570,DAT_0047b570);
      }
      uVar4 = 1;
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0047ae28,DAT_0047adcc,DAT_0047b480,0x41f,DAT_0047b574);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_0047b578,DAT_0047b578);
      }
      uVar4 = 0;
    }
  }
  return uVar4;
}

