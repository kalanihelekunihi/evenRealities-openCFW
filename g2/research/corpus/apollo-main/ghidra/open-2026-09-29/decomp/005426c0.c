
undefined8 SmpDbMaxAttemptReached(undefined1 param_1,undefined4 param_2)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  
  iVar2 = smpDbGetRecord(param_1);
  iVar3 = FUN_004c9c50();
  if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_005429f8,&DAT_0054282c,3), iVar3 != 0)) {
    iVar3 = FUN_004c9c50();
    if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_005429f8,DAT_0054295c,4), iVar3 != 0)) {
      iVar3 = FUN_004c9c50();
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(DAT_005429f8,DAT_005429f8,4), iVar3 != 0)) {
        iVar3 = FUN_004c9c50();
        if (iVar3 == 0) {
          iVar3 = FUN_004c9c50();
          if ((iVar3 == 0) || (iVar3 = FUN_0044b610(&DAT_00542830,&DAT_00542834,3), iVar3 != 0)) {
            WsfTrace(DAT_005429f8,PTR_s_SmpDbMaxAttemptReached__connId____00542a34,param_1);
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            param_2 = 0x121;
            FUN_0043d574(4,&DAT_00542830,DAT_00542958,PTR_s_SmpDbMaxAttemptReached_00542a38,0x121,
                         PTR_s_SmpDbMaxAttemptReached__connId____00542a34,param_1);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_2 = 0x121;
          FUN_0043d574(3,&DAT_00542830,DAT_00542958,PTR_s_SmpDbMaxAttemptReached_00542a38,0x121,
                       PTR_s_SmpDbMaxAttemptReached__connId____00542a34,param_1);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_2 = 0x121;
        FUN_0043d574(2,&DAT_00542830,DAT_00542958,PTR_s_SmpDbMaxAttemptReached_00542a38,0x121,
                     PTR_s_SmpDbMaxAttemptReached__connId____00542a34,param_1);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x121;
      FUN_0043d574(1,&DAT_00542830,DAT_00542958,PTR_s_SmpDbMaxAttemptReached_00542a38,0x121,
                   PTR_s_SmpDbMaxAttemptReached__connId____00542a34,param_1);
    }
  }
  piVar1 = DAT_00542a28;
  if (*(short *)(iVar2 + 8) == 0) {
    uVar4 = 1;
  }
  else {
    uVar4 = *(short *)(iVar2 + 8) * *(short *)(*DAT_00542a28 + 0x14);
  }
  if (*(uint *)(*DAT_00542a28 + 0xc) < (uint)uVar4 * *(int *)*DAT_00542a28) {
    *(undefined4 *)(iVar2 + 0xc) = *(undefined4 *)(*DAT_00542a28 + 0xc);
  }
  else {
    *(uint *)(iVar2 + 0xc) = (uint)uVar4 * *(int *)*DAT_00542a28;
    *(ushort *)(iVar2 + 8) = uVar4;
  }
  *(undefined4 *)(iVar2 + 0x10) = *(undefined4 *)(*piVar1 + 0x10);
  smpDbStartServiceTimer();
  return CONCAT44(param_2,*(undefined4 *)(iVar2 + 0xc));
}

