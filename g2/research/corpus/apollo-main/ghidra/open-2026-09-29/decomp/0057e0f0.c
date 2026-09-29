
undefined8 FUN_0057e0f0(int param_1,undefined4 param_2,uint param_3,uint param_4,uint param_5)

{
  undefined4 uVar1;
  uint local_18;
  uint uStack_14;
  
  uVar1 = *(undefined4 *)(param_1 + 4);
  local_18 = param_3;
  uStack_14 = param_4;
  if ((int)((uint)*(byte *)(param_1 + 0x1c) << 0x1f) < 0) {
    if (param_4 < param_5) {
      param_3 = 0;
    }
    else {
      uVar1 = FUN_0057e268(param_1,&local_18,4,uVar1);
    }
  }
  else if (param_4 <= param_3) {
    param_3 = param_4;
  }
  if (param_3 != 0) {
    uVar1 = FUN_0057e268(param_1,param_2,param_3,uVar1);
    *(undefined4 *)(param_1 + 4) = uVar1;
  }
  return CONCAT44(local_18,param_3);
}

