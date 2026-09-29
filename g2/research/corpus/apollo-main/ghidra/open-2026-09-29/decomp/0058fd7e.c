
undefined4 FUN_0058fd7e(int param_1,uint param_2)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = 10;
  if (param_2 == 0) {
    if (param_1 == 0) {
      uVar1 = 8;
    }
    else {
      uVar1 = 0xb;
    }
  }
  else if (param_2 == 2) {
    if (param_1 == 0) {
      uVar1 = 10;
    }
    else {
      uVar1 = 0xd;
    }
  }
  else if (param_2 < 2) {
    if (param_1 == 0) {
      uVar1 = 9;
    }
    else {
      uVar1 = 0xc;
    }
  }
  FUN_00539bbc(uVar1,0x11);
  return unaff_r7;
}

