
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057ea0a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 auStack_118 [4];
  undefined1 auStack_114 [256];
  undefined4 uStack_14;
  
  if (*_DAT_0057f270 == 1) {
    uStack_14 = param_4;
    pcVar2 = (char *)FUN_005848fc(param_3,1,auStack_118);
    iVar3 = FUN_0044a43c(pcVar2);
    iVar1 = _DAT_0057f3c4;
    iVar4 = FUN_0044a43c(_DAT_0057f3c4);
    if ((uint)(iVar4 + iVar3) < 0x101) {
      FUN_0043c0e4(auStack_114,0x100,0);
      uVar5 = FUN_0044a43c(iVar1);
      FUN_00439be4(auStack_114,iVar1,uVar5);
      iVar3 = FUN_0044a43c(iVar1);
      if ((*(char *)(iVar3 + iVar1 + -1) != '/') && (*pcVar2 != '/')) {
        FUN_00567c80(auStack_114,0x57eb8c);
      }
      uVar5 = FUN_00567c80(auStack_114,pcVar2);
      FUN_004cfa76(_DAT_0057f3c0,uVar5);
    }
    else {
      FUN_004733ee(_DAT_0057f3c8);
    }
  }
  return 0;
}

