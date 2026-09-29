
void FUN_0046137c(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int local_d8;
  int local_d4;
  int local_d0;
  int local_cc;
  int local_c8;
  int local_c4;
  undefined4 local_b8;
  undefined4 local_a8;
  undefined4 local_a0;
  undefined4 local_9c;
  int local_78;
  undefined4 local_74;
  undefined4 local_68;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 uStack_18;
  
  piVar2 = DAT_00461b10;
  piVar1 = DAT_004615d4;
  if (*DAT_00461b10 != 0) {
    uStack_18 = param_4;
    if (param_1 == '\0') {
      iVar3 = FUN_0044e4aa(*DAT_00461b10);
      iVar4 = *DAT_00461588 * (*DAT_00461590 + -5);
      if (iVar4 < 0) {
        iVar4 = 0;
      }
      iVar6 = iVar3 + 0x1e;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        local_d4 = DAT_00461618;
        local_d8 = 0x2d2;
        local_d0 = iVar3;
        local_cc = iVar6;
        local_c8 = iVar4;
        local_c4 = iVar4;
        FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_004615fc);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        local_d8 = iVar6;
        local_d4 = iVar4;
        local_d0 = iVar4;
        compress_log_output(0x11000000,DAT_0046161c,DAT_0046161c,iVar3);
      }
      FUN_004503d6(&local_d8);
      local_d8 = *piVar2;
      FUN_004506ce(&local_d8,iVar3,iVar6);
      local_a8 = 200;
      local_d4 = DAT_004615bc;
      local_b8 = DAT_00461610;
      local_9c = 200;
      local_a0 = 0;
      local_c8 = DAT_00461614;
      *DAT_004615b0 = 1;
      FUN_00450408(&local_d8);
    }
    else if (*DAT_004615d4 != 0) {
      iVar3 = FUN_0043fce0(*DAT_004615d4);
      if (iVar3 != 0) {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          local_d4 = DAT_004615f8;
          local_d8 = 0x2b2;
          local_d0 = iVar3;
          FUN_0043d574(2,DAT_00461e90,DAT_00461e8c,DAT_004615fc);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_00461600,DAT_00461600,iVar3);
        }
        FUN_0043f142(*piVar1,0);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_cc = 0x1e;
        local_d0 = 0;
        local_d4 = DAT_00461604;
        local_d8 = 0x2ba;
        FUN_0043d574(4,DAT_00461e90,DAT_00461e8c,DAT_004615fc);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        local_d8 = 0x1e;
        compress_log_output(0x10800000,DAT_00461608,DAT_00461608,0);
      }
      FUN_004503d6(&local_78);
      local_78 = *piVar1;
      FUN_004506ce(&local_78,0,0x1e);
      local_48 = 200;
      local_74 = DAT_0046160c;
      local_58 = DAT_00461610;
      local_3c = 200;
      local_40 = 0;
      local_68 = DAT_00461614;
      *DAT_004615b0 = 1;
      FUN_00450408(&local_78);
    }
  }
  return;
}

