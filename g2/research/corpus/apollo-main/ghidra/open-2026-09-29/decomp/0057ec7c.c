
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057ec7c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined1 auStack_118 [4];
  undefined1 auStack_114 [256];
  undefined4 uStack_14;
  
  if (*_DAT_0057f270 == 1) {
    uStack_14 = param_4;
    pcVar1 = (char *)FUN_005848fc(param_3,1,auStack_118);
    iVar2 = FUN_0044a43c(pcVar1);
    iVar5 = _DAT_0057f3c4;
    iVar3 = FUN_0044a43c(_DAT_0057f3c4);
    if ((uint)(iVar3 + iVar2) < 0x101) {
      FUN_0043c0e4(auStack_114,0x100,0);
      uVar4 = FUN_0044a43c(iVar5);
      FUN_00439be4(auStack_114,iVar5,uVar4);
      iVar2 = FUN_0044a43c(iVar5);
      if ((*(char *)(iVar2 + iVar5 + -1) != '/') && (*pcVar1 != '/')) {
        FUN_00567c80(auStack_114,0x57ee08);
      }
      uVar4 = FUN_00567c80(auStack_114,pcVar1);
      iVar5 = FUN_004cfc5c(_DAT_0057f3c0,uVar4);
      if (iVar5 != 0) {
        FUN_004733ee(_DAT_0057f938);
      }
    }
    else {
      FUN_004733ee(_DAT_0057f3c8);
    }
  }
  return 0;
}

