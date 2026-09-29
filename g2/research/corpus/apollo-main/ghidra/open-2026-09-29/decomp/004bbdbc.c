
undefined4 _PB_RxRingConnectInfoCommon(undefined1 param_1,char *param_2,char param_3)

{
  undefined1 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  if (param_2 == (char *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004bc7a4,DAT_004bc7a0,DAT_004bc79c,0x143,DAT_004bc798);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004bc7a8,DAT_004bc7a8);
    }
    uVar3 = 2;
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar1 = central_is_ring_owner_side_004a2914();
      iVar2 = FUN_0045a568();
      uVar3 = DAT_004bc4ac;
      if (iVar2 == 1) {
        uVar3 = DAT_004bc4a8;
      }
      FUN_0043d574(3,DAT_004bc7a4,DAT_004bc7a0,DAT_004bc79c,0x14b,DAT_004bc7ac,*param_2,param_3,
                   uVar3,uVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      uVar1 = central_is_ring_owner_side_004a2914();
      iVar2 = FUN_0045a568();
      uVar3 = DAT_004bc4ac;
      if (iVar2 == 1) {
        uVar3 = DAT_004bc4a8;
      }
      compress_log_output(0xd000000,DAT_004bc7b0,DAT_004bc7b0,*param_2,param_3,uVar3,uVar1);
    }
    FUN_0043dacc(DAT_004bc7b4,0x10,param_2 + 4,*(undefined2 *)(param_2 + 2));
    if ((param_3 == '\0') &&
       (iVar2 = RING_ConnectPolicyShouldBlockRingConnectInfo(*param_2), iVar2 != 0)) {
      uVar3 = 0;
    }
    else if ((*param_2 == '\0') || (iVar2 = central_is_ring_owner_side_004a2914(), iVar2 != 0)) {
      uVar3 = _PB_RxRingConnectInfoOwnerExecute(param_1,param_2);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_004bc7a4,DAT_004bc7a0,DAT_004bc79c,0x157,DAT_004bc7bc);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004bc90c,DAT_004bc90c);
      }
      uVar3 = 0;
    }
  }
  return uVar3;
}

