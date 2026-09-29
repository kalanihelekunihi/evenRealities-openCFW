
undefined4
hal_i2c_transfer_joined
          (byte param_1,byte param_2,undefined4 param_3,int param_4,undefined4 param_5,int param_6)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_70 [32];
  uint local_50 [4];
  int local_40;
  undefined1 local_3c;
  undefined1 *local_38;
  undefined1 local_30;
  undefined1 local_2e;
  
  FUN_0048949c(local_50,0x30);
  FUN_0043c0e4(auStack_70,0x20,0);
  iVar1 = DAT_00504768;
  if ((param_1 < 8) && ((uint)(param_6 + param_4) < 0x21)) {
    if (*(int *)(DAT_00504768 + (uint)param_1 * 4) != 0) {
      osMutexAcquire(*(undefined4 *)(DAT_00504768 + (uint)param_1 * 4),0xffffffff);
    }
    hal_i2c_power_down(param_1);
    FUN_00439be4(auStack_70,param_3,param_4);
    FUN_00439be4(auStack_70 + param_4,param_5,param_6);
    local_2e = 1;
    local_3c = 0;
    local_40 = param_6 + param_4;
    local_30 = 0;
    local_50[0] = (uint)param_2;
    local_38 = auStack_70;
    iVar3 = FUN_0055cc1c(*(undefined4 *)(DAT_00504760 + (uint)param_1 * 0x10 + 4),local_50);
    if (iVar3 == 0) {
      iVar3 = hal_i2c_power_up(param_1);
      if (*(int *)(iVar1 + (uint)param_1 * 4) != 0) {
        osMutexRelease(*(undefined4 *)(iVar1 + (uint)param_1 * 4));
      }
      if (iVar3 == 0) {
        uVar2 = 0;
      }
      else {
        uVar2 = 1;
      }
    }
    else {
      hal_i2c_power_up(param_1);
      if (*(int *)(iVar1 + (uint)param_1 * 4) != 0) {
        osMutexRelease(*(undefined4 *)(iVar1 + (uint)param_1 * 4));
      }
      uVar2 = 1;
    }
  }
  else {
    uVar2 = 1;
  }
  return uVar2;
}

