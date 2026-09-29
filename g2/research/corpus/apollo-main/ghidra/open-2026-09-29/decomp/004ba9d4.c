
undefined8
dmAdvConnected(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,&LAB_004bac28,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac68,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac80,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004bac64,&PTR_LAB_004baaf8,3), iVar1 != 0))
          {
            WsfTrace(PTR_DAT_004bac80,PTR_s_dmAdvConnected__state___d_004bacac,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_1 = 0x1ef;
            param_2 = PTR_s_dmAdvConnected__state___d_004bacac;
            FUN_0043d574(4,&DAT_004bac64,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                         PTR_s_dmAdvConnected_004bacb0,0x1ef,
                         PTR_s_dmAdvConnected__state___d_004bacac,
                         *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_1 = 0x1ef;
          param_2 = PTR_s_dmAdvConnected__state___d_004bacac;
          FUN_0043d574(3,&DAT_004bac64,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                       PTR_s_dmAdvConnected_004bacb0,0x1ef,PTR_s_dmAdvConnected__state___d_004bacac,
                       *(undefined1 *)(DAT_004bac7c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_1 = 0x1ef;
        param_2 = PTR_s_dmAdvConnected__state___d_004bacac;
        FUN_0043d574(2,&DAT_004bac64,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                     PTR_s_dmAdvConnected_004bacb0,0x1ef,PTR_s_dmAdvConnected__state___d_004bacac,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x1ef;
      param_2 = PTR_s_dmAdvConnected__state___d_004bacac;
      FUN_0043d574(1,&DAT_004bac64,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                   PTR_s_dmAdvConnected_004bacb0,0x1ef,PTR_s_dmAdvConnected__state___d_004bacac,
                   *(undefined1 *)(DAT_004bac7c + 0x1d),param_4);
    }
  }
  iVar1 = DAT_004bac7c;
  WsfTimerStop(DAT_004bac7c);
  dmDevPassEvtToDevPriv(0xd,0x22,0,0);
  *(undefined1 *)(iVar1 + 0x18) = 0xff;
  *(undefined1 *)(iVar1 + 0x1d) = 0;
  return CONCAT44(param_2,param_1);
}

