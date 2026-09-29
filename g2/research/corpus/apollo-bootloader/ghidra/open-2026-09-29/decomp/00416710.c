
undefined4 FUN_00416710(uint param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = param_1 & 0xfffffffe;
  uVar3 = 0;
  iVar1 = FUN_0041602a();
  if (iVar1 == 0) {
    if (uVar2 == 0) {
      uVar3 = 0xfffffffc;
    }
    else if ((param_1 & 1) == 0) {
      iVar1 = FUN_00419ec0(uVar2,0,0,0);
      if (iVar1 != 1) {
        uVar3 = 0xfffffffd;
      }
    }
    else {
      iVar1 = FUN_00419de2(uVar2);
      if (iVar1 != 1) {
        uVar3 = 0xfffffffd;
      }
    }
  }
  else {
    uVar3 = 0xfffffffa;
  }
  return uVar3;
}

