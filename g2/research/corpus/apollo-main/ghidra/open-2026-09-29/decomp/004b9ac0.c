
undefined8 dmAdvActConfig(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,&DAT_004b9d1c,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,DAT_004ba6c4,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b9d20,&DAT_004b9e7c,3), iVar1 != 0)) {
            WsfTrace(PTR_DAT_004ba4a0,PTR_s_dmAdvActConfig__state___d_004ba4a4,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0x6f;
            param_2 = PTR_s_dmAdvActConfig__state___d_004ba4a4;
            FUN_0043d574(4,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActConfig_004ba4a8,0x6f,PTR_s_dmAdvActConfig__state___d_004ba4a4
                         ,*(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0x6f;
          param_2 = PTR_s_dmAdvActConfig__state___d_004ba4a4;
          FUN_0043d574(3,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActConfig_004ba4a8,0x6f,PTR_s_dmAdvActConfig__state___d_004ba4a4,
                       *(undefined1 *)(DAT_004ba49c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar2 = 0x6f;
        param_2 = PTR_s_dmAdvActConfig__state___d_004ba4a4;
        FUN_0043d574(2,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                     PTR_s_dmAdvActConfig_004ba4a8,0x6f,PTR_s_dmAdvActConfig__state___d_004ba4a4,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0x6f;
      param_2 = PTR_s_dmAdvActConfig__state___d_004ba4a4;
      FUN_0043d574(1,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                   PTR_s_dmAdvActConfig_004ba4a8,0x6f,PTR_s_dmAdvActConfig__state___d_004ba4a4,
                   *(undefined1 *)(DAT_004ba49c + 0x1d),param_4);
    }
  }
  if (*(char *)(DAT_004ba49c + 0x1d) == '\0') {
    if ((*(char *)(DAT_004ba49c + 0x18) == '\x01') || (*(char *)(DAT_004ba49c + 0x18) == '\x04')) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004ba6c4,&DAT_004b9d1c,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004ba6c4,DAT_004ba6c4,4), iVar1 != 0)) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_004ba6c4,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b9d20,&DAT_004b9e7c,3), iVar1 != 0))
              {
                WsfTrace(DAT_004ba6c4,DAT_004ba6d0);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                iVar2 = 0x77;
                param_2 = DAT_004ba6d0;
                FUN_0043d574(4,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                             PTR_s_dmAdvActConfig_004ba4a8);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              iVar2 = 0x77;
              param_2 = DAT_004ba6d0;
              FUN_0043d574(3,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                           PTR_s_dmAdvActConfig_004ba4a8);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0x77;
            param_2 = DAT_004ba6d0;
            FUN_0043d574(2,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActConfig_004ba4a8);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0x77;
          param_2 = DAT_004ba6d0;
          FUN_0043d574(1,&DAT_004b9d20,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActConfig_004ba4a8);
        }
      }
    }
    else {
      dmAdvConfig(*(undefined1 *)(param_1 + 5),*(undefined1 *)(param_1 + 6),param_1 + 7);
    }
  }
  return CONCAT44(param_2,iVar2);
}

