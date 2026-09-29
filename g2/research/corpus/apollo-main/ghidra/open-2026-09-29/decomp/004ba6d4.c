
undefined8 dmAdvStartDirected(uint param_1,undefined *param_2,undefined1 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  uint uVar3;
  undefined *puVar4;
  undefined4 uVar5;
  
  uVar3 = param_1;
  puVar4 = param_2;
  uVar5 = param_4;
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004bac80,&DAT_004ba854,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004ba860,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac80,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_004ba9c8,&PTR_LAB_004ba848,3), iVar2 != 0))
          {
            WsfTrace(PTR_DAT_004bac80,PTR_s_dmAdvStartDirected__state___d_004bac98,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            uVar3 = 0x1bd;
            puVar4 = PTR_s_dmAdvStartDirected__state___d_004bac98;
            FUN_0043d574(4,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                         PTR_s_dmAdvStartDirected_004bac9c,0x1bd,
                         PTR_s_dmAdvStartDirected__state___d_004bac98,
                         *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar3 = 0x1bd;
          puVar4 = PTR_s_dmAdvStartDirected__state___d_004bac98;
          FUN_0043d574(3,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                       PTR_s_dmAdvStartDirected_004bac9c,0x1bd,
                       PTR_s_dmAdvStartDirected__state___d_004bac98,
                       *(undefined1 *)(DAT_004bac7c + 0x1d));
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0x1bd;
        puVar4 = PTR_s_dmAdvStartDirected__state___d_004bac98;
        FUN_0043d574(2,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                     PTR_s_dmAdvStartDirected_004bac9c,0x1bd,
                     PTR_s_dmAdvStartDirected__state___d_004bac98,
                     *(undefined1 *)(DAT_004bac7c + 0x1d));
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar3 = 0x1bd;
      puVar4 = PTR_s_dmAdvStartDirected__state___d_004bac98;
      FUN_0043d574(1,&DAT_004ba9c8,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                   PTR_s_dmAdvStartDirected_004bac9c,0x1bd,
                   PTR_s_dmAdvStartDirected__state___d_004bac98,*(undefined1 *)(DAT_004bac7c + 0x1d)
                   ,uVar5);
    }
  }
  iVar2 = DAT_004bac7c;
  if (*(char *)(DAT_004bac7c + 0x1d) == '\0') {
    HciLeSetAdvEnableCmd(1);
    if ((param_1 & 0xff) == 1) {
      uVar1 = 2;
    }
    else {
      uVar1 = 3;
    }
    *(undefined1 *)(iVar2 + 0x1d) = uVar1;
    *(short *)(iVar2 + 0x20) = (short)param_2;
    FUN_004d293c(iVar2 + 0x25,param_4);
    *(undefined1 *)(iVar2 + 0x31) = param_3;
  }
  return CONCAT44(puVar4,uVar3);
}

