
undefined4 FUN_004894d0(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else if (param_1 - 0x4e00U < 0x5200) {
    uVar1 = 1;
  }
  else if (param_1 - 0xff01U < 0x5e) {
    uVar1 = 1;
  }
  else if (param_1 - 0x3000U < 0x40) {
    uVar1 = 1;
  }
  else if (param_1 - 0x2e80U < 0x80) {
    uVar1 = 1;
  }
  else if (param_1 - 0x31c0U < 0x30) {
    uVar1 = 1;
  }
  else if (param_1 - 0x3040U < 0xc0) {
    uVar1 = 1;
  }
  else if ((uint)(DAT_00489e98 + param_1) < 0x10) {
    uVar1 = 1;
  }
  else if ((uint)(DAT_00489e9c + param_1) < 0x20) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

