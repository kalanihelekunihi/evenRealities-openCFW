
undefined4 hal_i2c_transfer_read(byte param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_48 [4];
  undefined4 local_38;
  undefined1 local_34;
  undefined4 local_2c;
  undefined1 local_28;
  undefined1 local_26;
  
  FUN_0048949c(local_48,0x30);
  iVar1 = DAT_00504768;
  if (param_1 < 8) {
    if (*(int *)(DAT_00504768 + (uint)param_1 * 4) != 0) {
      osMutexAcquire(*(undefined4 *)(DAT_00504768 + (uint)param_1 * 4),0xffffffff);
    }
    hal_i2c_power_down(param_1);
    local_26 = 1;
    local_34 = 1;
    local_28 = 0;
    local_48[0] = (uint)param_2;
    local_38 = param_4;
    local_2c = param_3;
    iVar3 = FUN_0055cc1c(*(undefined4 *)(DAT_00504760 + (uint)param_1 * 0x10 + 4),local_48);
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

