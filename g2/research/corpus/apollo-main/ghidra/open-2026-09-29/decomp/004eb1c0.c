
void FUN_004eb1c0(int param_1,int param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  undefined4 local_58;
  int local_48;
  
  iVar1 = DAT_004eb740;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_74 = DAT_004eb7ac;
      local_78 = 0x33f;
      FUN_0043d574(1,DAT_004eb32c,DAT_004eb328,DAT_004eb7b0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004eb7b4,DAT_004eb7b4);
    }
  }
  else {
    *(undefined1 *)(DAT_004eb740 + 0x124) = 0;
    iVar2 = FUN_0044e498(param_1);
    if (param_2 == iVar2) {
      param_3 = 10;
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_70 = 10;
        local_74 = DAT_004ebdd8;
        local_78 = 0x347;
        FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb7b0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004ebddc,DAT_004ebddc,10);
      }
    }
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_74 = DAT_004ebde0;
      local_78 = 0x34b;
      local_70 = iVar2;
      local_6c = param_2;
      local_68 = param_3;
      FUN_0043d574(4,DAT_004eb32c,DAT_004eb328,DAT_004eb7b0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      local_78 = param_2;
      local_74 = param_3;
      compress_log_output(0x10c00000,DAT_004ebde4,DAT_004ebde4,iVar2);
    }
    if (param_3 == 0) {
      FUN_0044ea04(param_1,param_2,0);
    }
    else {
      FUN_004503d6(&local_78);
      local_78 = param_1;
      FUN_004506ce(&local_78,iVar2,param_2);
      local_74 = DAT_004ebde8;
      local_68 = DAT_004ebdec;
      local_58 = DAT_004ebf28;
      *(undefined1 *)(iVar1 + 0x124) = 1;
      local_48 = param_3;
      FUN_00450408(&local_78);
    }
  }
  return;
}

