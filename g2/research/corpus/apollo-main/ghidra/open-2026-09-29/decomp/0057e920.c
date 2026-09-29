
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057e920(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_130 [4];
  undefined1 auStack_12c [64];
  undefined1 auStack_ec [128];
  undefined1 auStack_6c [84];
  undefined4 uStack_18;
  
  if (*_DAT_0057f270 == 1) {
    uStack_18 = param_4;
    pcVar1 = (char *)FUN_005848fc(param_3,1,auStack_130);
    iVar2 = FUN_0044a43c(pcVar1);
    iVar6 = _DAT_0057f3c4;
    iVar3 = FUN_0044a43c(_DAT_0057f3c4);
    if ((uint)(iVar3 + iVar2) < 0x81) {
      FUN_0043c0e4(auStack_ec,0x80,0);
      uVar4 = FUN_0044a43c(iVar6);
      FUN_00439be4(auStack_ec,iVar6,uVar4);
      iVar2 = FUN_0044a43c(iVar6);
      if ((*(char *)(iVar2 + iVar6 + -1) != '/') && (*pcVar1 != '/')) {
        FUN_00567c80(auStack_ec,0x57eb8c);
      }
      uVar5 = FUN_00567c80(auStack_ec,pcVar1);
      uVar4 = _DAT_0057f3c0;
      iVar6 = FUN_004cfa94(_DAT_0057f3c0,auStack_6c,uVar5,1);
      if (iVar6 == 0) {
        while( true ) {
          FUN_0043c0e4(auStack_12c,0x40,0);
          iVar6 = FUN_004cfb40(uVar4,auStack_6c,auStack_12c,0x40);
          if ((iVar6 < 0) || (iVar6 == 0)) break;
          for (iVar2 = 0; iVar2 < iVar6; iVar2 = iVar2 + 1) {
            FUN_005415d8(auStack_12c[iVar2]);
          }
        }
        FUN_004cfad0(uVar4,auStack_6c);
      }
    }
    else {
      FUN_004733ee(_DAT_0057f3c8);
    }
  }
  return 0;
}

