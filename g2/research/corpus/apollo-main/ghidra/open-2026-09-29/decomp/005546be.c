
int FUN_005546be(int param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined1 auStack_24 [4];
  int local_20;
  int iStack_1c;
  
  iStack_1c = param_4;
  if (param_1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_00554d3c,DAT_00554d38,DAT_005551dc,0x187,DAT_005551d8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005551e0,DAT_005551e0);
    }
    iVar1 = 0;
  }
  else {
    FUN_0043c0e4(auStack_24,8,0);
    FUN_0044e75e(param_1,auStack_24);
    iVar2 = FUN_0044e4bc(param_1);
    iVar2 = iVar2 + local_20;
    iVar1 = param_2;
    if (100 < param_3) {
      iVar1 = param_2 << 1;
    }
    if (iVar1 < 1) {
      iVar4 = local_20;
      if (iVar1 < 0) {
        iVar4 = param_4 * ((iVar1 + local_20) / param_4);
      }
    }
    else {
      iVar4 = param_4 * ((param_4 + iVar1 + local_20 + -1) / param_4);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_005551dc,0x1a8,DAT_005551e4,param_2,param_3,
                   local_20,iVar2,iVar4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x11400000,DAT_005551e8,DAT_005551e8,param_2,param_3,local_20,iVar2,iVar4)
      ;
    }
    if (iVar2 < 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_005551dc,0x1aa,DAT_005551ec);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_005551f0,DAT_005551f0);
      }
      iVar1 = 0;
    }
    else if (iVar4 < 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_005551dc,0x1b0,DAT_005551f4,iVar4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_005551f8,DAT_005551f8,iVar4);
      }
      iVar1 = 0;
    }
    else {
      iVar1 = iVar4;
      if (iVar2 < iVar4) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00554d3c,DAT_00554d38,DAT_005551dc,0x1b5,DAT_005551fc,iVar4,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        iVar1 = iVar2;
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00555458,DAT_00555458,iVar4,iVar2);
        }
      }
    }
  }
  return iVar1;
}

