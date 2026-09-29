
undefined4 FUN_00489ee0(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 0x20) {
    uVar1 = 1;
  }
  else if (param_1 == 0x61c) {
    uVar1 = 1;
  }
  else if (param_1 == 0x115f) {
    uVar1 = 1;
  }
  else if (param_1 == 0x1160) {
    uVar1 = 1;
  }
  else if (DAT_0048a934 + param_1 < 4) {
    uVar1 = 1;
  }
  else if (DAT_0048a938 + param_1 < 5) {
    uVar1 = 1;
  }
  else if (DAT_0048a93c + param_1 < 8) {
    uVar1 = 1;
  }
  else if (DAT_0048a940 + param_1 < 0x11) {
    uVar1 = 1;
  }
  else if (param_1 == 0xfeff) {
    uVar1 = 1;
  }
  else if (param_1 == 0xf8ff) {
    uVar1 = 1;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

