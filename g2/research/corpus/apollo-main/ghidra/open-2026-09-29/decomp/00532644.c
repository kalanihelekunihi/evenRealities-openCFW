
undefined8 FUN_00532644(int param_1,undefined *param_2)

{
  char cVar1;
  ushort uVar2;
  int iVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  
  iVar4 = *(int *)(param_2 + 4);
  uVar2 = *(ushort *)(param_2 + 8);
  cVar1 = **(char **)(param_2 + 4);
  pbVar5 = (byte *)(*(char **)(param_2 + 4) + 1);
  while (pbVar5 < (byte *)(iVar4 + (uint)uVar2)) {
    iVar6 = (uint)pbVar5[1] * 0x100 + (uint)*pbVar5;
    if (cVar1 == '\x01') {
      iVar7 = (uint)pbVar5[3] * 0x100 + (uint)pbVar5[2];
      pbVar5 = pbVar5 + 4;
      if (iVar7 == 0x2900) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          param_1 = 0x253;
          param_2 = DAT_00533298;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,0x253,DAT_00533298,0x2900,iVar6);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_0053329c,DAT_0053329c,0x2900);
          param_1 = iVar6;
        }
      }
      else if (iVar7 == 0x2901) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          param_1 = 600;
          param_2 = DAT_005332a0;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,600,DAT_005332a0,0x2901,iVar6);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_005332a4,DAT_005332a4,0x2901);
          param_1 = iVar6;
        }
      }
      else if (iVar7 == 0x2902) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          param_1 = 0x24e;
          param_2 = DAT_0053328c;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,0x24e,DAT_0053328c,0x2902,iVar6);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00533290,DAT_00533290,0x2902);
          param_1 = iVar6;
        }
      }
      else if (iVar7 == 0x2908) {
        iVar7 = FUN_0043d0ce();
        if (iVar7 << 0x1e < 0) {
          param_1 = 0x25d;
          param_2 = DAT_005332a8;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,0x25d,DAT_005332a8,0x2908,iVar6);
        }
        iVar7 = FUN_0043d0ce();
        if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_005332ac,DAT_005332ac,0x2908);
          param_1 = iVar6;
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_1 = 0x262;
          param_2 = DAT_005332b0;
          FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,0x262,DAT_005332b0,iVar7,iVar6);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00533454,DAT_00533454,iVar7);
          param_1 = iVar6;
        }
      }
    }
    else {
      iVar7 = FUN_0043d0ce();
      if (iVar7 << 0x1e < 0) {
        param_1 = 0x268;
        param_2 = DAT_00533024;
        FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028,0x268,DAT_00533024,iVar6);
      }
      iVar7 = FUN_0043d0ce();
      if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_00533030,DAT_00533030,iVar6);
      }
      FUN_0043dacc(DAT_00533034,0x10,pbVar5 + 2,0x10);
      pbVar5 = pbVar5 + 0x12;
      iVar6 = FUN_0043d0ce();
      if (iVar6 << 0x1e < 0) {
        param_2 = &DAT_00532910;
        param_1 = 0x26b;
        FUN_0043d574(4,DAT_00532e8c,DAT_0053302c,DAT_00533028);
      }
      iVar6 = FUN_0043d0ce();
      if ((iVar6 << 0x1f < 0) || (iVar6 = FUN_0043d0ce(), iVar6 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_00533038,DAT_00533038);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

