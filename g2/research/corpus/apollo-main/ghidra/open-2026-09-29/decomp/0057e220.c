
undefined8 FUN_0057e220(undefined4 *param_1,undefined4 param_2,uint param_3,uint param_4)

{
  uint uVar1;
  undefined4 uVar2;
  uint local_18;
  
  uVar2 = *param_1;
  uVar1 = param_3;
  local_18 = param_4;
  if ((int)((uint)*(byte *)(param_1 + 7) << 0x1f) < 0) {
    uVar2 = FUN_0057e2f6(param_1,&local_18,4,uVar2);
    param_4 = param_4 - 4;
    uVar1 = local_18;
    if (param_3 < local_18) {
      uVar1 = 0;
    }
  }
  if (uVar1 < param_4) {
    param_4 = uVar1;
  }
  if (param_4 != 0) {
    uVar2 = FUN_0057e2f6(param_1,param_2,param_4,uVar2);
    *param_1 = uVar2;
  }
  return CONCAT44(local_18,param_4);
}

