
void CALLBACK_MGR_Unregister(int *param_1,int param_2)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  
  if (param_1 == (int *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_005105a0,0x87,DAT_0051055c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510564);
    }
  }
  else if (param_2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00510554,DAT_00510550,DAT_005105a0,0x8c,DAT_00510580);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00510584,DAT_00510584);
    }
  }
  else if (*param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00510554,DAT_00510550,DAT_005105a0,0x91,DAT_005105a4,param_1[2]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005105a8,DAT_005105a8,param_1[2]);
    }
  }
  else {
    piVar1 = (int *)*param_1;
    piVar4 = (int *)0x0;
    while (piVar3 = piVar1, piVar3 != (int *)0x0) {
      if (*piVar3 == param_2) {
        if (piVar4 == (int *)0x0) {
          *param_1 = piVar3[1];
        }
        else {
          piVar4[1] = piVar3[1];
        }
        callback_mgr_delete_node();
        *(char *)(param_1 + 1) = (char)param_1[1] + -1;
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00510554,DAT_00510550,DAT_005105a0,0xa9,DAT_005105ac,param_1[2],
                       (char)param_1[1]);
        }
        iVar2 = FUN_0043d0ce();
        if ((-1 < iVar2 << 0x1f) && (iVar2 = FUN_0043d0ce(), -1 < iVar2 << 0x1d)) {
          return;
        }
        compress_log_output(0x10800000,DAT_005105b0,DAT_005105b0,param_1[2],(char)param_1[1]);
        return;
      }
      piVar4 = piVar3;
      piVar1 = (int *)piVar3[1];
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00510554,DAT_00510550,DAT_005105a0,0xb0,DAT_005105b4,param_1[2]);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_005105b8,DAT_005105b8,param_1[2]);
    }
  }
  return;
}

