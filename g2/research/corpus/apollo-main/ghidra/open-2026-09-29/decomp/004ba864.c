
undefined8 dmAdvStopDirected(void)

{
  int iVar1;
  undefined1 uVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,&DAT_004ba9cc,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac68,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac80,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004ba9c8,&PTR_LAB_004baaf8,3), iVar1 != 0))
          {
            WsfTrace(PTR_DAT_004bac80,PTR_s_dmAdvStopDirected__state___d_004baca0,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            unaff_r5 = 0x1d8;
            unaff_r6 = PTR_s_dmAdvStopDirected__state___d_004baca0;
            FUN_0043d574(4,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                         PTR_s_dmAdvStopDirected_004baca4,0x1d8,
                         PTR_s_dmAdvStopDirected__state___d_004baca0,
                         *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          unaff_r5 = 0x1d8;
          unaff_r6 = PTR_s_dmAdvStopDirected__state___d_004baca0;
          FUN_0043d574(3,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                       PTR_s_dmAdvStopDirected_004baca4,0x1d8,
                       PTR_s_dmAdvStopDirected__state___d_004baca0,
                       *(undefined1 *)(DAT_004bac7c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 0x1d8;
        unaff_r6 = PTR_s_dmAdvStopDirected__state___d_004baca0;
        FUN_0043d574(2,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                     PTR_s_dmAdvStopDirected_004baca4,0x1d8,
                     PTR_s_dmAdvStopDirected__state___d_004baca0,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 0x1d8;
      unaff_r6 = PTR_s_dmAdvStopDirected__state___d_004baca0;
      FUN_0043d574(1,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                   PTR_s_dmAdvStopDirected_004baca4,0x1d8,
                   PTR_s_dmAdvStopDirected__state___d_004baca0,*(undefined1 *)(DAT_004bac7c + 0x1d))
      ;
    }
  }
  if (((*(char *)(DAT_004bac7c + 0x1d) == '\x01') || (*(char *)(DAT_004bac7c + 0x1d) == '\x03')) ||
     (*(char *)(DAT_004bac7c + 0x1d) == '\x02')) {
    if (*DAT_004baca8 == '\x01') {
      uVar2 = 4;
    }
    else {
      uVar2 = 5;
    }
    *(undefined1 *)(DAT_004bac7c + 0x1d) = uVar2;
    HciLeSetAdvEnableCmd(0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

