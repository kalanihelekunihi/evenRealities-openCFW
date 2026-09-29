
void FUN_004f6e6c(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  undefined4 local_58;
  int local_48;
  
  if (param_1 != 0) {
    FUN_0043f66c(*DAT_004f747c);
    iVar1 = FUN_0044e498(param_1);
    if (param_2 == iVar1) {
      param_3 = 10;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_70 = 10;
        local_74 = DAT_004f7930;
        local_78 = 0x76a;
        FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7934);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004f7938,DAT_004f7938,10);
      }
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_74 = DAT_004f793c;
      local_78 = 0x76e;
      local_70 = iVar1;
      local_6c = param_2;
      local_68 = param_3;
      FUN_0043d574(4,DAT_004f758c,DAT_004f7588,DAT_004f7934);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      local_78 = param_2;
      local_74 = param_3;
      compress_log_output(0x10c00000,DAT_004f7940,DAT_004f7940,iVar1);
    }
    if (param_3 < 1) {
      FUN_0044ea04(param_1,param_2,0);
    }
    else {
      FUN_004503d6(&local_78);
      local_78 = param_1;
      FUN_004506ce(&local_78,iVar1,param_2);
      local_74 = DAT_004f778c;
      if (param_4 != 0) {
        local_68 = param_4;
      }
      local_58 = DAT_004f792c;
      *DAT_004f6fb8 = 1;
      local_48 = param_3;
      FUN_00450408(&local_78);
    }
    return;
  }
  return;
}

