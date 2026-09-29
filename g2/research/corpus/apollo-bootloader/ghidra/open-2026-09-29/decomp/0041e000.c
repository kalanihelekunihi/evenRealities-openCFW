
undefined4 FUN_0041e000(char param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = DAT_0041e1e0;
  uVar3 = param_2 >> 5;
  iVar4 = uVar3 + 7;
  if (param_1 == '\0') {
    *(undefined4 *)(DAT_0041e1e0 + uVar3 * 0x80 + (param_2 & 0x1f) * 4) = param_3;
    *(undefined4 *)(DAT_0041e1e4 + uVar3 * 0x80 + (param_2 & 0x1f) * 4) = param_4;
  }
  else if (param_1 == '\x01') {
    *(undefined4 *)(DAT_0041e1e0 + iVar4 * 0x80 + (param_2 & 0x1f) * 4) = param_3;
    *(undefined4 *)(DAT_0041e1e4 + iVar4 * 0x80 + (param_2 & 0x1f) * 4) = param_4;
  }
  else {
    if (param_1 != '\x02') {
      return 6;
    }
    *(undefined4 *)(uVar3 * 0x80 + DAT_0041e1e0 + (param_2 & 0x1f) * 4) = param_3;
    iVar2 = DAT_0041e1e4;
    *(undefined4 *)(uVar3 * 0x80 + DAT_0041e1e4 + (param_2 & 0x1f) * 4) = param_4;
    *(undefined4 *)(iVar1 + iVar4 * 0x80 + (param_2 & 0x1f) * 4) = param_3;
    *(undefined4 *)(iVar2 + iVar4 * 0x80 + (param_2 & 0x1f) * 4) = param_4;
  }
  return 0;
}

