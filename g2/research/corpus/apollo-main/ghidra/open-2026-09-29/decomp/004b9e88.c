
undefined8 dmAdvActStart(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = param_1;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,&DAT_004ba0e8,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba860,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004ba0ec,&DAT_004ba0f0,3), iVar1 != 0)) {
            WsfTrace(PTR_DAT_004ba4a0,PTR_s_dmAdvActStart__state___d_004ba858,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0xaa;
            param_2 = PTR_s_dmAdvActStart__state___d_004ba858;
            FUN_0043d574(4,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActStart_004ba85c,0xaa,PTR_s_dmAdvActStart__state___d_004ba858,
                         *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0xaa;
          param_2 = PTR_s_dmAdvActStart__state___d_004ba858;
          FUN_0043d574(3,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActStart_004ba85c,0xaa,PTR_s_dmAdvActStart__state___d_004ba858,
                       *(undefined1 *)(DAT_004ba49c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar2 = 0xaa;
        param_2 = PTR_s_dmAdvActStart__state___d_004ba858;
        FUN_0043d574(2,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                     PTR_s_dmAdvActStart_004ba85c,0xaa,PTR_s_dmAdvActStart__state___d_004ba858,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      iVar2 = 0xaa;
      param_2 = PTR_s_dmAdvActStart__state___d_004ba858;
      FUN_0043d574(1,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                   PTR_s_dmAdvActStart_004ba85c,0xaa,PTR_s_dmAdvActStart__state___d_004ba858,
                   *(undefined1 *)(DAT_004ba49c + 0x1d),param_4);
    }
  }
  iVar1 = DAT_004ba49c;
  if (*(char *)(DAT_004ba49c + 0x1d) == '\0') {
    if ((*(char *)(DAT_004ba49c + 0x18) == '\x01') || (*(char *)(DAT_004ba49c + 0x18) == '\x04')) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba860,&DAT_004ba0e8,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba860,PTR_DAT_004ba860,4), iVar1 != 0))
        {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) ||
             (iVar1 = FUN_0044b610(PTR_DAT_004ba860,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004ba0ec,&DAT_004ba0f0,3), iVar1 != 0))
              {
                WsfTrace(PTR_DAT_004ba860,DAT_004ba9d0);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                iVar2 = 0xb2;
                param_2 = DAT_004ba9d0;
                FUN_0043d574(4,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                             PTR_s_dmAdvActStart_004ba85c);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              iVar2 = 0xb2;
              param_2 = DAT_004ba9d0;
              FUN_0043d574(3,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                           PTR_s_dmAdvActStart_004ba85c);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar2 = 0xb2;
            param_2 = DAT_004ba9d0;
            FUN_0043d574(2,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActStart_004ba85c);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar2 = 0xb2;
          param_2 = DAT_004ba9d0;
          FUN_0043d574(1,&DAT_004ba0ec,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActStart_004ba85c);
        }
      }
    }
    else {
      *(undefined1 *)(DAT_004ba49c + 0x1d) = 3;
      *(undefined2 *)(iVar1 + 0x20) = *(undefined2 *)(param_1 + 8);
      HciLeSetAdvEnableCmd(1);
    }
  }
  return CONCAT44(param_2,iVar2);
}

