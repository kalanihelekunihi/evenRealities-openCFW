
undefined8 als_function_20(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = als_function_02();
  uVar2 = uVar1;
  if (uVar1 < param_2) {
    uVar2 = param_2;
  }
  if (uVar2 < 100) {
    if (param_2 <= uVar1) {
      param_2 = uVar1;
    }
  }
  else {
    param_2 = 100;
  }
  uVar2 = param_1 - uVar1;
  if (uVar1 < param_2) {
    param_2 = param_2 - uVar1;
  }
  else {
    param_2 = 0;
  }
  if (uVar2 == 0) {
    uVar1 = 0x400;
  }
  else {
    uVar1 = FUN_0047cc60(param_2 * 0x400 + (uVar2 >> 1),
                         (param_2 >> 0x16) + (uint)CARRY4(param_2 * 0x400,uVar2 >> 1),uVar2,0);
    uVar2 = uVar1;
    if (uVar1 < 0x267) {
      uVar2 = 0x266;
    }
    if (uVar2 < 0x59a) {
      if (uVar1 < 0x267) {
        uVar1 = 0x266;
      }
    }
    else {
      uVar1 = 0x59a;
    }
  }
  return CONCAT44(param_4,uVar1);
}

