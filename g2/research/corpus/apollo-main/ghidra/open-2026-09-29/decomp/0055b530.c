
int FUN_0055b530(int param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_14;
  
  local_14 = param_4;
  FUN_0043c0e4(&local_14,2,0,param_4,param_1,param_2,param_3);
  if ((param_1 == 0) || (param_2 == (undefined2 *)0x0)) {
    iVar1 = -1;
  }
  else {
    iVar1 = (**(code **)(param_1 + 4))(8,&local_14,2);
    if (iVar1 == 0) {
      *param_2 = (undefined2)local_14;
      iVar1 = FUN_0055b3ea(param_2);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0055b9d4,DAT_0055b9d0,DAT_0055b9e8,0xf9,DAT_0055b9e4,*param_2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0055b9ec,DAT_0055b9ec,*param_2);
        }
        iVar1 = 0xff;
      }
      else {
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}

