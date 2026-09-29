
undefined4 FUN_00593bf8(ushort *param_1)

{
  undefined4 uVar1;
  
  if (((param_1[1] & 0xf800) == 0xf800) && ((*param_1 & 0xf800) == 0xf000)) {
    uVar1 = 1;
  }
  else if ((param_1[1] & 0xff00) == 0x4700) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

