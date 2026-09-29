
undefined4 FUN_00508ed2(uint param_1,int param_2)

{
  uint uVar1;
  undefined4 uVar2;
  
  param_2 = param_2 + param_1;
  uVar1 = param_2 - 1;
  if (((param_1 - 0x2400 < 0x1c00) || (param_2 - 0x2401U < 0x1c00)) ||
     ((param_1 < 0x2400 && (0x3fff < uVar1)))) {
    uVar2 = 0xfffffffd;
  }
  else if (((param_1 - 0x8400 < 0x1c00) || (param_2 - 0x8401U < 0x1c00)) ||
          ((param_1 < 0x8400 && (0x9fff < uVar1)))) {
    uVar2 = 0xfffffffd;
  }
  else if (uVar1 < 0xb000) {
    uVar2 = 0;
  }
  else {
    uVar2 = 0xfffffffd;
  }
  return uVar2;
}

