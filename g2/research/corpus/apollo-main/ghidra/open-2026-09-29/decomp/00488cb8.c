
undefined4 FUN_00488cb8(byte *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (byte *)0x0) {
    uVar1 = 3;
  }
  else if (*param_1 - 0x20 < 0x60) {
    uVar1 = 1;
  }
  else if (*param_1 < 0x80) {
    uVar1 = 0;
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

