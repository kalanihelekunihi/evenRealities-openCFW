
undefined8 FUN_005dd39e(int param_1,uint param_2)

{
  undefined4 uVar1;
  uint local_8;
  
  local_8 = param_2;
  if (param_2 < 0x10000) {
    if ((int)((uint)*(byte *)(param_1 + 0x14) << 0x1f) < 0) {
      uVar1 = FUN_005dce22(param_1,&local_8,0);
    }
    else {
      uVar1 = FUN_005dcff6(param_1,&local_8,0);
    }
  }
  else {
    uVar1 = 0;
  }
  return CONCAT44(local_8,uVar1);
}

