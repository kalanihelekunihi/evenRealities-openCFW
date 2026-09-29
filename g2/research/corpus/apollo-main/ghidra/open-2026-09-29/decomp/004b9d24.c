
undefined8 dmAdvActSetData(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,&DAT_004b9e80,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,DAT_004ba6c4,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b9e84,&DAT_004b9e7c,3), iVar1 != 0)) {
            WsfTrace(PTR_DAT_004ba4a0,PTR_s_dmAdvActSetData__state___d_004ba84c,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0x8f;
            param_2 = PTR_s_dmAdvActSetData__state___d_004ba84c;
            FUN_0043d574(4,&DAT_004b9e84,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActSetData_004ba850,0x8f,
                         PTR_s_dmAdvActSetData__state___d_004ba84c,
                         *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0x8f;
          param_2 = PTR_s_dmAdvActSetData__state___d_004ba84c;
          FUN_0043d574(3,&DAT_004b9e84,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActSetData_004ba850,0x8f,PTR_s_dmAdvActSetData__state___d_004ba84c
                       ,*(undefined1 *)(DAT_004ba49c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar2 = 0x8f;
        param_2 = PTR_s_dmAdvActSetData__state___d_004ba84c;
        FUN_0043d574(2,&DAT_004b9e84,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                     PTR_s_dmAdvActSetData_004ba850,0x8f,PTR_s_dmAdvActSetData__state___d_004ba84c,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x8f;
      param_2 = PTR_s_dmAdvActSetData__state___d_004ba84c;
      FUN_0043d574(1,&DAT_004b9e84,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                   PTR_s_dmAdvActSetData_004ba850,0x8f,PTR_s_dmAdvActSetData__state___d_004ba84c,
                   *(undefined1 *)(DAT_004ba49c + 0x1d),param_4);
    }
  }
  if (*(char *)(DAT_004ba49c + 0x1d) == '\0') {
    if (*(char *)(param_1 + 6) == '\0') {
      HciLeSetAdvDataCmd(*(undefined1 *)(param_1 + 7),param_1 + 8);
    }
    else {
      HciLeSetScanRespDataCmd(*(undefined1 *)(param_1 + 7),param_1 + 8);
    }
  }
  return CONCAT44(param_2,iVar2);
}

