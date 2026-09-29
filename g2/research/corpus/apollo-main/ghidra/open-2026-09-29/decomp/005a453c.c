
undefined8 FUN_005a453c(uint param_1,uint param_2,int param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint local_20;
  int iStack_1c;
  
  local_20 = CONCAT31((int3)((uint)param_3 >> 8),0x1a);
  iStack_1c = param_4;
  if (param_1 == param_2) {
    if (param_3 != param_4) {
      FUN_005a423c(param_3,param_1);
    }
  }
  else if (param_1 >> 2 == param_2 >> 2) {
    FUN_005a44ba(param_1,param_2,param_3,param_4);
  }
  else {
    uVar2 = param_2;
    if ((param_1 & 3) != (param_2 & 3)) {
      uVar2 = param_1 & 3 | param_2 & 0xfffffffc;
      FUN_005a44ba(uVar2,param_2,param_3,param_4);
    }
    iVar1 = FUN_005a4334(param_1,uVar2,&local_20);
    if (iVar1 == 0) {
      (**(code **)(DAT_005a4e60 + (local_20 & 0xff) * 4))(param_1,uVar2,param_3,param_4);
    }
  }
  return CONCAT44(iStack_1c,local_20);
}

