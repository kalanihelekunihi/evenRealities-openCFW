
uint FUN_004e8bcc(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  int local_70;
  int local_6c;
  uint local_68;
  int local_64;
  int local_60;
  undefined4 local_50;
  undefined4 local_40;
  undefined4 uStack_10;
  
  piVar2 = DAT_004e9390;
  piVar1 = DAT_004e8db4;
  uStack_10 = param_4;
  if (param_1 == 10) {
    uVar4 = *DAT_004e939c;
    if (uVar4 == 0) {
      if (*DAT_004e9390 == 0) {
        if ((*(int *)(DAT_004e8da8 + 0x14) == 0) || (*DAT_004e8db4 == 0)) {
          uVar4 = 0;
        }
        else {
          FUN_0043dfa4(*DAT_004e8db4,1);
          FUN_004503d6(&local_70);
          local_70 = *piVar1;
          FUN_004506ce(&local_70,0x160,0x240);
          local_40 = 0xfa;
          local_6c = DAT_004e93b0;
          local_50 = DAT_004e9388;
          local_60 = DAT_004e93b4;
          *piVar2 = 1;
          *DAT_004e93bc = *DAT_004e93b8;
          uVar4 = FUN_00450408(&local_70);
        }
      }
      else {
        uVar4 = 1;
      }
    }
  }
  else if (param_1 == 0x44) {
    uVar4 = *DAT_004e939c;
    if (uVar4 == 0) {
      uVar4 = FUN_004e7d20(1);
    }
  }
  else if (param_1 == 0x45) {
    uVar4 = *DAT_004e939c;
    if (uVar4 == 0) {
      uVar4 = FUN_004e7d20(0xffffffff);
    }
  }
  else if (param_1 == 0x46) {
    uVar4 = *DAT_004e939c;
    if (uVar4 == 0) {
      uVar4 = FUN_004e7dfa(param_2);
    }
  }
  else if ((param_1 == 0x48) || (param_1 == 0x49)) {
    uVar4 = *DAT_004e939c;
    if (uVar4 == 0) {
      if (*DAT_004e9390 == 0) {
        uVar4 = FUN_004e8a90();
      }
      else {
        uVar4 = 1;
      }
    }
  }
  else if (param_1 == 0x4a) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_60 = *DAT_004e9390;
      local_64 = *DAT_004e93a0;
      local_68 = *DAT_004e939c;
      local_6c = DAT_004e93a4;
      local_70 = 0x559;
      FUN_0043d574(3,DAT_004e9370,DAT_004e936c,DAT_004e93a8);
    }
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1f) {
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1d) {
        return iVar3 << 0x1d;
      }
    }
    local_6c = *DAT_004e9390;
    local_70 = *DAT_004e93a0;
    uVar4 = compress_log_output(0xcc00000,DAT_004e93ac,DAT_004e93ac,*DAT_004e939c);
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_68 = (uint)param_1;
      local_6c = DAT_004e93c0;
      local_70 = 0x590;
      FUN_0043d574(2,DAT_004e9370,DAT_004e936c,DAT_004e93a8);
    }
    iVar3 = FUN_0043d0ce();
    if (-1 < iVar3 << 0x1f) {
      iVar3 = FUN_0043d0ce();
      if (-1 < iVar3 << 0x1d) {
        return iVar3 << 0x1d;
      }
    }
    uVar4 = compress_log_output(0x8400000,PTR_s__dashborad_ui_unknown_Dashboard__004e93c4,
                                PTR_s__dashborad_ui_unknown_Dashboard__004e93c4,param_1);
  }
  return uVar4;
}

