
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_0057eb94(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  undefined1 auStack_24c [4];
  undefined1 auStack_248 [52];
  undefined1 auStack_214 [256];
  undefined1 auStack_114 [256];
  undefined4 uStack_14;
  
  if (*_DAT_0057f270 == 1) {
    uStack_14 = param_4;
    pcVar3 = (char *)FUN_005848fc(param_3,1,auStack_24c);
    iVar4 = FUN_0044a43c(pcVar3);
    iVar2 = _DAT_0057f3c4;
    iVar5 = FUN_0044a43c(_DAT_0057f3c4);
    if ((uint)(iVar5 + iVar4) < 0x100) {
      FUN_0043c0e4(auStack_114,0xff,0);
      if ((pcVar3 == (char *)0x0) || (uVar6 = FUN_0044a43c(pcVar3), 0xfe < uVar6)) {
        FUN_004733ee(_DAT_0057f8b4);
      }
      else {
        if (*pcVar3 == '/') {
          FUN_0044b728(auStack_114,0xff,0x57ee04,pcVar3);
        }
        else {
          FUN_0044b728(auStack_114,0xff,_DAT_0057f688,iVar2,pcVar3);
        }
        iVar4 = FUN_0057eaa8(auStack_214,auStack_114);
        uVar1 = _DAT_0057f3c0;
        if (iVar4 == 0) {
          iVar4 = FUN_004cfc66(_DAT_0057f3c0,auStack_248,auStack_214);
          if (iVar4 == 0) {
            FUN_004cfcf8(uVar1,auStack_248);
            FUN_0044b5a0(iVar2,auStack_214,0x80);
            *(undefined1 *)(iVar2 + 0x7f) = 0;
          }
          else {
            FUN_004733ee(_DAT_0057f8b4);
          }
        }
        else {
          FUN_004733ee(_DAT_0057f8b4);
        }
      }
    }
    else {
      FUN_004733ee(_DAT_0057f3c8);
    }
  }
  return 0;
}

