
void FUN_005e49b0(char param_1,char param_2,undefined4 param_3)

{
  int iVar1;
  undefined1 uVar2;
  
  iVar1 = DAT_005e53b4;
  if ((((*(int *)(DAT_005e53b4 + 0x1cc) != 0) && (*(int *)(DAT_005e53b4 + 0x1d0) != 0)) &&
      (*(int *)(DAT_005e53b4 + 0x1d4) != 0)) && (*(int *)(DAT_005e53b4 + 0x1dc) != 0)) {
    FUN_0043dfa4(*(undefined4 *)(DAT_005e53b4 + 0x1cc),1);
    FUN_005ea30c();
    FUN_005e482a(*(undefined4 *)(iVar1 + 0x1d0),DAT_005e5558,6,100);
    if (param_1 == '\0') {
      if (param_2 != '\0') {
        if (*DAT_005e5564 == '\0') {
          FUN_0049942e(*(undefined4 *)(iVar1 + 0x1d4),DAT_005e5568);
        }
        else {
          FUN_005ea2a8(*DAT_005e5560);
        }
      }
    }
    else {
      uVar2 = FUN_005ea2a8(param_3);
      *DAT_005e555c = param_3;
      *DAT_005e5560 = uVar2;
      *DAT_005e5564 = '\x01';
    }
    FUN_0049942e(*(undefined4 *)(iVar1 + 0x1dc),DAT_005e556c);
    FUN_005e4902();
  }
  return;
}

