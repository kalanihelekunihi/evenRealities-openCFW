
undefined4 _log_get_all_buffer(int param_1,ushort param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 unaff_r6;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  piVar2 = DAT_0043d0e8;
  iVar5 = *DAT_0043d0e8;
  uVar6 = DAT_0043d0e8[1];
  uVar7 = DAT_0043d0e8[2];
  uVar8 = DAT_0043d0e8[3];
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0043d0f8,DAT_0043d0f4,DAT_0043d0f0,0x7a,DAT_0043d0ec,uVar7,uVar8,uVar6,
                 param_2,param_4);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0xd000000,DAT_0043d0fc,DAT_0043d0fc,uVar7,uVar8,uVar6,param_2);
  }
  if ((uVar6 < uVar7) || (uVar6 < uVar8)) {
    uVar4 = 0;
  }
  else {
    if (uVar8 < uVar7) {
      iVar3 = uVar6 - uVar7;
    }
    else {
      iVar3 = -uVar7;
    }
    if (uVar8 + iVar3 < (uint)param_2) {
      uVar4 = 0;
    }
    else {
      uVar8 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar8 = getCurrentExceptionNumber();
        uVar8 = uVar8 & 0x1ff;
      }
      if (uVar8 == 0) {
        FUN_004420d0();
      }
      else {
        unaff_r6 = ulSetInterruptMask();
      }
      uVar6 = uVar6 - uVar7;
      if (uVar6 < param_2) {
        FUN_00439be4(param_1,iVar5 + uVar7,uVar6);
        FUN_00439be4(param_1 + uVar6,iVar5,param_2 - uVar6);
      }
      else {
        FUN_00439be4(param_1,iVar5 + uVar7,param_2);
      }
      if (param_2 < uVar6) {
        iVar3 = uVar7 + param_2;
      }
      else {
        iVar3 = param_2 - uVar6;
      }
      piVar2[2] = iVar3;
      uVar6 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar6 = getCurrentExceptionNumber();
        uVar6 = uVar6 & 0x1ff;
      }
      if (uVar6 == 0) {
        FUN_004420e8();
      }
      else {
        vClearInterruptMask(unaff_r6);
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(4,DAT_0043d0f8,DAT_0043d0f4,DAT_0043d0f0,0x97,DAT_0043d100,param_2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0043d104,DAT_0043d104,param_2);
      }
      uVar4 = 1;
    }
  }
  return uVar4;
}

