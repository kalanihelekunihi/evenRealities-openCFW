
undefined4 FUN_005d2170(int param_1,uint param_2)

{
  undefined4 uVar1;
  
  if (param_1 == 1) {
    uVar1 = 0;
  }
  else if (param_2 < 0x4d8) {
    uVar1 = 0x6b;
  }
  else if (param_2 < 0x846c) {
    uVar1 = 0x46b;
  }
  else {
    uVar1 = 0x8000;
  }
  return uVar1;
}

