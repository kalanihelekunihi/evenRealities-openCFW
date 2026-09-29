
undefined8 dmAdvActTimeout(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004ba4a0,&DAT_004ba490,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004ba4a0,DAT_004ba6c4,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba4a0,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004ba494,&LAB_004ba458,3), iVar2 != 0)) {
            WsfTrace(PTR_DAT_004ba4a0,PTR_s_dmAdvActTimeout__004bac74);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          puVar1 = PTR_s_dmAdvActTimeout__004bac74;
          if (iVar2 << 0x1e < 0) {
            unaff_r5 = 0x10f;
            FUN_0043d574(4,&DAT_004ba494,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActTimeout_004bac78);
            unaff_r6 = puVar1;
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        puVar1 = PTR_s_dmAdvActTimeout__004bac74;
        if (iVar2 << 0x1e < 0) {
          unaff_r5 = 0x10f;
          FUN_0043d574(3,&DAT_004ba494,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActTimeout_004bac78);
          unaff_r6 = puVar1;
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      puVar1 = PTR_s_dmAdvActTimeout__004bac74;
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x10f;
        FUN_0043d574(2,&DAT_004ba494,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                     PTR_s_dmAdvActTimeout_004bac78);
        unaff_r6 = puVar1;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_dmAdvActTimeout__004bac74;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x10f;
      FUN_0043d574(1,&DAT_004ba494,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                   PTR_s_dmAdvActTimeout_004bac78);
      unaff_r6 = puVar1;
    }
  }
  if (*(char *)(DAT_004bac7c + 0x1d) == '\x01') {
    *(undefined1 *)(DAT_004bac7c + 0x1d) = 5;
    HciLeSetAdvEnableCmd(0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

