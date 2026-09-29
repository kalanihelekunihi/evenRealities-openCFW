
undefined8 dmAdvActStop(void)

{
  int iVar1;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,&DAT_004ba334,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004bac68,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004ba4a0,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004ba338,&LAB_004ba458,3), iVar1 != 0)) {
            WsfTrace(PTR_DAT_004ba4a0,PTR_s_dmAdvActStop__state___d_004baafc,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            unaff_r5 = 200;
            unaff_r6 = PTR_s_dmAdvActStop__state___d_004baafc;
            FUN_0043d574(4,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActStop_004bab00,200,PTR_s_dmAdvActStop__state___d_004baafc,
                         *(undefined1 *)(DAT_004ba49c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          unaff_r5 = 200;
          unaff_r6 = PTR_s_dmAdvActStop__state___d_004baafc;
          FUN_0043d574(3,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActStop_004bab00,200,PTR_s_dmAdvActStop__state___d_004baafc,
                       *(undefined1 *)(DAT_004ba49c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        unaff_r5 = 200;
        unaff_r6 = PTR_s_dmAdvActStop__state___d_004baafc;
        FUN_0043d574(2,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                     PTR_s_dmAdvActStop_004bab00,200,PTR_s_dmAdvActStop__state___d_004baafc,
                     *(undefined1 *)(DAT_004ba49c + 0x1d));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      unaff_r5 = 200;
      unaff_r6 = PTR_s_dmAdvActStop__state___d_004baafc;
      FUN_0043d574(1,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                   PTR_s_dmAdvActStop_004bab00,200,PTR_s_dmAdvActStop__state___d_004baafc,
                   *(undefined1 *)(DAT_004ba49c + 0x1d));
    }
  }
  if (*(char *)(DAT_004ba49c + 0x1d) == '\x01') {
    if ((*(char *)(DAT_004ba49c + 0x18) == '\x01') || (*(char *)(DAT_004ba49c + 0x18) == '\x04')) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac68,&DAT_004ba334,3), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac68,PTR_DAT_004bac68,4), iVar1 != 0))
        {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) ||
             (iVar1 = FUN_0044b610(PTR_DAT_004bac68,PTR_DAT_004ba4a0,4), iVar1 != 0)) {
            iVar1 = FUN_004c9c50();
            if (iVar1 == 0) {
              iVar1 = FUN_004c9c50();
              if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004ba338,&LAB_004ba458,3), iVar1 != 0))
              {
                WsfTrace(PTR_DAT_004bac68,PTR_s_DmAdvStop_during_directed_advert_004bac6c);
              }
            }
            else {
              iVar1 = FUN_0043d0ce();
              if (iVar1 << 0x1e < 0) {
                unaff_r5 = 0xd0;
                unaff_r6 = PTR_s_DmAdvStop_during_directed_advert_004bac6c;
                FUN_0043d574(4,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                             PTR_s_dmAdvActStop_004bab00);
              }
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              unaff_r5 = 0xd0;
              unaff_r6 = PTR_s_DmAdvStop_during_directed_advert_004bac6c;
              FUN_0043d574(3,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                           PTR_s_dmAdvActStop_004bab00);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            unaff_r5 = 0xd0;
            unaff_r6 = PTR_s_DmAdvStop_during_directed_advert_004bac6c;
            FUN_0043d574(2,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                         PTR_s_dmAdvActStop_004bab00);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          unaff_r5 = 0xd0;
          unaff_r6 = PTR_s_DmAdvStop_during_directed_advert_004bac6c;
          FUN_0043d574(1,&DAT_004ba338,PTR_s_D__01_workspace_s200_ap510b_iar__004ba4ac,
                       PTR_s_dmAdvActStop_004bab00);
        }
      }
    }
    else {
      *(undefined1 *)(DAT_004ba49c + 0x1d) = 5;
      HciLeSetAdvEnableCmd(0);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

