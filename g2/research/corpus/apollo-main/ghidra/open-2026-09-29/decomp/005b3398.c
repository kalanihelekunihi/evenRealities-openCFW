
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_005b3398(char param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  byte bVar4;
  
  FUN_005b3340(*_DAT_005b3530);
  iVar1 = _DAT_005b3514;
  if (((param_1 == '\x04') || (param_1 == '\x05')) && (*(int *)(_DAT_005b3514 + 0x1c) != 0)) {
    FUN_0044d7b8(*(undefined4 *)(_DAT_005b3514 + 0x1c));
    *(undefined4 *)(iVar1 + 0x1c) = 0;
  }
  iVar1 = _DAT_005b3514;
  if (*(char *)(_DAT_005b3514 + 0x8c) == '\0') {
    FUN_0043ded4(*(undefined4 *)(_DAT_005b3514 + 100),1);
  }
  else {
    FUN_0043dfa4(*(undefined4 *)(_DAT_005b3514 + 100),1);
    FUN_00441488(*(undefined4 *)(iVar1 + 100),0xff,0);
  }
  if (*(char *)(iVar1 + 0x8d) == '\0') {
    FUN_0043ded4(*(undefined4 *)(iVar1 + 0x20),1);
  }
  else {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x20),1);
  }
  FUN_0043dfa4(*(undefined4 *)(iVar1 + 8),1);
  FUN_00441488(*(undefined4 *)(iVar1 + 8),0xff,0);
  bVar2 = FUN_0044ddea(*(undefined4 *)(iVar1 + 100));
  for (bVar4 = 0; bVar4 < bVar2; bVar4 = bVar4 + 1) {
    iVar3 = FUN_0044dce2(*(undefined4 *)(iVar1 + 100),bVar4);
    if (iVar3 != 0) {
      FUN_0043dfa4(iVar3,1);
      FUN_00441488(iVar3,0xff,0);
      FUN_005b1072(iVar3,0);
    }
  }
  *(undefined4 *)(iVar1 + 0x80) = 0;
  *(undefined4 *)(iVar1 + 0x84) = 0;
  *(undefined1 *)(iVar1 + 0x96) = 0;
  FUN_005b0edc(0,0,PTR_s_display_config_005b356c);
  if (*(int *)(iVar1 + 0x7c) != 0) {
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x7c),1);
    FUN_00441488(*(undefined4 *)(iVar1 + 0x7c),0xff,0);
    FUN_005b1072(*(undefined4 *)(iVar1 + 0x7c),0);
  }
  return (ulonglong)param_4 << 0x20;
}

