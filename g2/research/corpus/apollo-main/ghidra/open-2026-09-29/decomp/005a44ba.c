
undefined8 FUN_005a44ba(uint param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint local_20;
  undefined4 uStack_1c;
  
  local_20 = CONCAT31((int3)((uint)param_3 >> 8),0x1a);
  uVar2 = param_2;
  uStack_1c = param_4;
  if (param_2 < param_1) {
    for (; uVar2 < param_1; uVar2 = uVar2 + 1) {
      iVar1 = FUN_005a4334(uVar2 + 1,uVar2,&local_20);
      if (iVar1 == 0) {
        (**(code **)(DAT_005a4e60 + (local_20 & 0xff) * 4))(param_1,param_2,param_3,param_4);
      }
    }
  }
  else {
    for (; param_1 < uVar2; uVar2 = uVar2 - 1) {
      iVar1 = FUN_005a4334(uVar2 - 1,uVar2,&local_20);
      if (iVar1 == 0) {
        (**(code **)(DAT_005a4e60 + (local_20 & 0xff) * 4))(param_1,param_2,param_3,param_4);
      }
    }
  }
  return CONCAT44(uStack_1c,local_20);
}

