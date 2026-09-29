
void _bleCommHandler(undefined1 param_1,short *param_2)

{
  undefined1 uVar1;
  int iVar2;
  
  if (param_2 != (short *)0x0) {
    if (*(byte *)(param_2 + 1) - 2 < 0x17) {
      FUN_00532924(param_2);
      FUN_0053484c(param_2);
    }
    else if (*(byte *)(param_2 + 1) - 0x20 < 0x5c) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar1 = DmConnRole((char)*param_2);
        FUN_0043d574(4,DAT_004b8210,DAT_004b820c,DAT_004b847c,0x28b,DAT_004b8478,*param_2,uVar1);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        uVar1 = DmConnRole((char)*param_2);
        compress_log_output(0x10800000,DAT_004b8480,DAT_004b8480,*param_2,uVar1);
      }
      if ((*param_2 == 0) || (iVar2 = DmConnRole((char)*param_2), iVar2 == 0)) {
        FUN_00503b92(param_2);
        FUN_00503c32(param_2);
      }
      if ((*param_2 == 0) || (iVar2 = DmConnRole((char)*param_2), iVar2 == 1)) {
        iVar2 = dmConnGetAdvState();
        if ((iVar2 == 0) || ((char)param_2[1] != '\"')) {
          FUN_004b3ca4(param_2);
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(3,DAT_004b8210,DAT_004b820c,DAT_004b847c,0x29a,DAT_004b8484);
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004b8720,DAT_004b8720);
          }
        }
        FUN_004b45b0(param_2);
      }
      FUN_005322bc(param_2);
    }
    bleProcMsg(param_2);
    dmConnSmEventDispatch(param_1,param_2);
    ring_dm_event_dispatch(param_1,param_2);
  }
  return;
}

