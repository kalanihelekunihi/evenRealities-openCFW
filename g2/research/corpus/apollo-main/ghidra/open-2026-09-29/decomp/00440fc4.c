
undefined4 FUN_00440fc4(byte param_1)

{
  uint uVar1;
  undefined4 uVar2;
  
  uVar1 = (uint)param_1;
  if (((uVar1 - 7 < 8) || (uVar1 == 0x10)) || (uVar1 - 0x13 < 6)) {
    uVar2 = 1;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

