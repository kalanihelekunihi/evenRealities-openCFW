
undefined4 Cy_Flash_ValidAddr(uint param_1)

{
  undefined4 uVar1;
  
  if (param_1 < 0x10000) {
    if ((param_1 & 0x7f) == 0) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  else if (param_1 + DAT_00008ca4 < 0x200) {
    if ((param_1 & 0x7f) == 0) {
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

