
undefined4
FUN_0052fcfc(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  if (param_1 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x180,DAT_00530038);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00530040,DAT_00530040);
    }
    uVar3 = 0;
  }
  else {
    uVar4 = FUN_0052f3a0(1);
    uVar3 = DAT_00530048;
    piVar1 = DAT_00530044;
    iVar2 = file_open(DAT_00530048,uVar4);
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = -1;
    }
    else {
      iVar2 = 0;
    }
    if (iVar2 == 0) {
      uVar6 = FUN_0052f3f8(*piVar1);
      if ((int)uVar6 < 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x18e,DAT_0052ff54);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0052ff58,DAT_0052ff58);
        }
        if (*piVar1 != 0) {
          file_close(*piVar1);
          *piVar1 = 0;
        }
        uVar3 = 0;
      }
      else if (uVar6 < 0x10) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x195,DAT_00530054,uVar6,0x10);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_00530058,DAT_00530058,uVar6,0x10);
        }
        if (*piVar1 != 0) {
          file_close(*piVar1);
          *piVar1 = 0;
        }
        uVar3 = 0;
      }
      else {
        iVar2 = file_read(&local_28,1,0x10,*piVar1);
        if (iVar2 == 0x10) {
          if (*piVar1 != 0) {
            file_close(*piVar1);
            *piVar1 = 0;
          }
          *param_1 = local_28;
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x1a8,DAT_00530064,local_28,
                         local_24,local_20,local_1c);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x11000000,DAT_00530068,DAT_00530068,local_28,local_24,local_20,
                                local_1c);
          }
          uVar3 = 1;
        }
        else {
          iVar5 = FUN_0043d0ce();
          if (iVar5 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x19e,DAT_0053005c,iVar2,0x10);
          }
          iVar5 = FUN_0043d0ce();
          if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_00530060,DAT_00530060,iVar2,0x10);
          }
          if (*piVar1 != 0) {
            file_close(*piVar1);
            *piVar1 = 0;
          }
          uVar3 = 0;
        }
      }
    }
    else {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0052ff50,DAT_0052ff4c,DAT_0053003c,0x187,DAT_0053004c,uVar3,iVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_00530050,DAT_00530050,uVar3,iVar2);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

