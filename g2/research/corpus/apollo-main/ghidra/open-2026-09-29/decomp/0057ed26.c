
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057ed26(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int iVar6;
  undefined1 auStack_168 [4];
  undefined1 auStack_164 [256];
  undefined1 auStack_64 [84];
  
  if (*_DAT_0057f270 == 1) {
    pcVar1 = (char *)FUN_005848fc(param_3,1,auStack_168);
    iVar2 = FUN_0044a43c(pcVar1);
    iVar6 = _DAT_0057f3c4;
    iVar3 = FUN_0044a43c(_DAT_0057f3c4);
    if ((uint)(iVar3 + iVar2) < 0x101) {
      FUN_0043c0e4(auStack_164,0x100,0);
      uVar4 = FUN_0044a43c(iVar6);
      FUN_00439be4(auStack_164,iVar6,uVar4);
      iVar2 = FUN_0044a43c(iVar6);
      if ((*(char *)(iVar2 + iVar6 + -1) != '/') && (*pcVar1 != '/')) {
        FUN_00567c80(auStack_164,0x57ee08);
      }
      uVar5 = FUN_00567c80(auStack_164,pcVar1);
      uVar4 = _DAT_0057f3c0;
      iVar6 = FUN_004cfa94(_DAT_0057f3c0,auStack_64,uVar5,0x102);
      if (iVar6 == 0) {
        FUN_004cfad0(uVar4,auStack_64);
      }
      else {
        FUN_004733ee(_DAT_0057f938);
      }
    }
    else {
      FUN_004733ee(_DAT_0057f3c8);
    }
  }
  return 0;
}

