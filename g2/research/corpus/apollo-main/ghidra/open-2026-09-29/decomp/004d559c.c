
undefined4 FUN_004d559c(uint param_1)

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
  else if (DAT_004d5848 + param_1 < 4) {
    uVar1 = 1;
  }
  else if (DAT_004d584c + param_1 < 5) {
    uVar1 = 1;
  }
  else if (DAT_004d5850 + param_1 < 8) {
    uVar1 = 1;
  }
  else if (DAT_004d5854 + param_1 < 0x11) {
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

