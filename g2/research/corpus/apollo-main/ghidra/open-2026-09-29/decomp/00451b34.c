
undefined4 FUN_00451b34(undefined4 *param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((*(byte *)(param_1 + 6) & 7) >> 2 == 0) {
    if (param_1[2] - 0x2b < 2) {
      uVar1 = 1;
    }
    else {
      iVar2 = FUN_0043e0e0(*param_1,0x4000);
      if (iVar2 == 0) {
        uVar1 = 0;
      }
      else {
        iVar2 = param_1[2];
        if ((((iVar2 == 0x16) || (iVar2 - 0x1aU < 9)) || (iVar2 == 0x25)) ||
           (((iVar2 - 0x29U < 4 || (iVar2 - 0x31U < 2)) || (iVar2 - 0x31U == 3)))) {
          uVar1 = 0;
        }
        else {
          uVar1 = 1;
        }
      }
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

