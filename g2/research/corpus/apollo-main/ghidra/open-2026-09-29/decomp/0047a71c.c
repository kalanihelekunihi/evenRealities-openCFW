
int FUN_0047a71c(undefined1 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  uint uVar4;
  char cVar5;
  uint uVar6;
  int iVar7;
  
  iVar7 = DAT_0047ae64;
  uVar4 = param_3;
  iVar3 = FUN_0047a676(param_3 & 0xff);
  if (4 < iVar3) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar4 = DAT_0047a8a8;
      if ((param_3 & 0xff) != 0) {
        uVar4 = DAT_0047a8a4;
      }
      FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047ae6c,0x396,DAT_0047ae68,uVar4,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar6 = DAT_0047a8a8;
      if ((param_3 & 0xff) != 0) {
        uVar6 = DAT_0047a8a4;
      }
      compress_log_output(0x10400000,DAT_0047ae70,DAT_0047ae70,uVar6);
    }
    iVar3 = FUN_0047a6b4(param_3 & 0xff);
    if (iVar3 != 0) {
      DmPrivRemDevFromResList(*(undefined1 *)(iVar3 + 6),iVar3,0);
      FUN_0047a47c(iVar3);
    }
  }
  cVar5 = '\n';
  while( true ) {
    if (cVar5 == '\0') {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0047ae28,DAT_0047adcc,DAT_0047ae6c,0x3b3,DAT_0047ae74,uVar4,param_4);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_0047b4ac,DAT_0047b4ac);
      }
      return 0;
    }
    if (*(char *)(iVar7 + 0x2f) == '\0') break;
    cVar5 = cVar5 + -1;
    iVar7 = iVar7 + 200;
  }
  FUN_0043c0e4(iVar7,200,0);
  *(undefined1 *)(iVar7 + 0x2f) = 1;
  uVar2 = DmHostAddrType(param_1);
  *(undefined1 *)(iVar7 + 6) = uVar2;
  FUN_004d293c(iVar7,param_2);
  *(char *)(iVar7 + 0xc3) = (char)param_3;
  piVar1 = DAT_0047ae50;
  *DAT_0047ae50 = *DAT_0047ae50 + 1;
  *(int *)(iVar7 + 0xc4) = *piVar1;
  return iVar7;
}

