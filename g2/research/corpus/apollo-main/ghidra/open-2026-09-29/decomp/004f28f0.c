
void FUN_004f28f0(int param_1,int param_2)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  int local_74;
  undefined4 local_70;
  undefined4 local_64;
  undefined4 local_54;
  int local_44;
  
  piVar2 = DAT_004f3374;
  piVar1 = DAT_004f3368;
  if ((param_1 < 0) || (*DAT_004f3250 <= param_1)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3264,0x5a5,DAT_004f3260,param_1,*DAT_004f3250
                  );
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_004f3268,DAT_004f3268,param_1,*DAT_004f3250);
    }
  }
  else if (*DAT_004f3368 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3264,0x5aa,DAT_004f336c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004f3370,DAT_004f3370);
    }
  }
  else {
    FUN_004f0e94(*DAT_004f3374);
    *piVar2 = param_1;
    uVar4 = FUN_004f2804(param_1);
    if (param_2 == 0) {
      FUN_0044ea04(*piVar1,uVar4,0);
      FUN_004f0e18(param_1);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3264,0x5cb,DAT_004f3390,param_1,uVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10800000,DAT_004f3394,DAT_004f3394,param_1,uVar4);
      }
    }
    else {
      FUN_004503d6(&local_74);
      local_74 = *piVar1;
      local_70 = DAT_004f3378;
      uVar5 = FUN_0044e498(*piVar1);
      FUN_004506ce(&local_74,uVar5,uVar4);
      local_54 = DAT_004f337c;
      local_64 = DAT_004f3380;
      *DAT_004f3384 = 1;
      local_44 = param_2;
      FUN_00450408(&local_74);
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004f2eb4,DAT_004f2eb0,DAT_004f3264,0x5c6,DAT_004f3388,param_1,uVar4,
                     param_2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10c00000,DAT_004f338c,DAT_004f338c,param_1,uVar4,param_2);
      }
    }
  }
  return;
}

