
undefined4 FUN_00489b74(byte *param_1)

{
  undefined4 uVar1;
  
  if ((int)((uint)*param_1 << 0x18) < 0) {
    if ((*param_1 & 0xe0) == 0xc0) {
      uVar1 = 2;
    }
    else if ((*param_1 & 0xf0) == 0xe0) {
      uVar1 = 3;
    }
    else if ((*param_1 & 0xf8) == 0xf0) {
      uVar1 = 4;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

