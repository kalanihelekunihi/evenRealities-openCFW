
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 dmAdvHciHandler(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  char cVar2;
  int iVar3;
  
  iVar3 = param_1;
  if (*(char *)(param_1 + 2) == '5') {
    cVar2 = '\0';
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,0x4ba6c8,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,DAT_004ba6c4,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_004bac80,PTR_DAT_004bac80,4), iVar1 != 0))
        {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(0x4ba6cc,&PTR_LAB_004ba848,3), iVar1 != 0)) {
              WsfTrace(PTR_DAT_004bac80,PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84,
                       *(undefined1 *)(DAT_004bac7c + 0x1d));
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              iVar3 = 0x147;
              param_2 = PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84;
              FUN_0043d574(4,0x4ba6cc,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                           PTR_s_dmAdvHciHandler_004bac88,0x147,
                           PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84,
                           *(undefined1 *)(DAT_004bac7c + 0x1d));
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            iVar3 = 0x147;
            param_2 = PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84;
            FUN_0043d574(3,0x4ba6cc,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                         PTR_s_dmAdvHciHandler_004bac88,0x147,
                         PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84,
                         *(undefined1 *)(DAT_004bac7c + 0x1d));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          iVar3 = 0x147;
          param_2 = PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84;
          FUN_0043d574(2,0x4ba6cc,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                       PTR_s_dmAdvHciHandler_004bac88,0x147,
                       PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84,
                       *(undefined1 *)(DAT_004bac7c + 0x1d));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        iVar3 = 0x147;
        param_2 = PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84;
        FUN_0043d574(1,0x4ba6cc,PTR_s_D__01_workspace_s200_ap510b_iar__004bac8c,
                     PTR_s_dmAdvHciHandler_004bac88,0x147,
                     PTR_s_HCI_LE_ADV_ENABLE_CMD_CMPL_CBACK_004bac84,
                     *(undefined1 *)(DAT_004bac7c + 0x1d),param_4);
      }
    }
    iVar1 = DAT_004bac7c;
    if (*(byte *)(DAT_004bac7c + 0x1d) - 2 < 2) {
      if (*(char *)(param_1 + 3) == '\0') {
        if (*(char *)(DAT_004bac7c + 0x1d) == '\x03') {
          if (*(short *)(DAT_004bac7c + 0x20) != 0) {
            *(undefined1 *)(DAT_004bac7c + 10) = 7;
            WsfTimerStartMs(iVar1,*(undefined2 *)(iVar1 + 0x20));
          }
          if (*DAT_004ba6c0 != '\x04') {
            cVar2 = '!';
          }
        }
        dmDevPassEvtToDevPriv(0xc,0x21,0,0);
        *(char *)(iVar1 + 0x18) = *DAT_004ba6c0;
        *(undefined1 *)(iVar1 + 0x1d) = 1;
      }
      else {
        *(undefined1 *)(DAT_004bac7c + 0x1d) = 0;
      }
    }
    else if (*(byte *)(DAT_004bac7c + 0x1d) - 4 < 2) {
      if (*(char *)(param_1 + 3) == '\0') {
        if (*(char *)(DAT_004bac7c + 0x1d) == '\x05') {
          WsfTimerStop(DAT_004bac7c);
          if (*DAT_004ba6c0 == '\x04') {
            cVar2 = '\x02';
          }
          else {
            cVar2 = '\"';
          }
        }
        dmDevPassEvtToDevPriv(0xd,0x22,0,0);
        *(undefined1 *)(iVar1 + 0x18) = 0xff;
        *(undefined1 *)(iVar1 + 0x1d) = 0;
      }
      else {
        *(undefined1 *)(DAT_004bac7c + 0x1d) = 1;
      }
    }
    if (cVar2 == '\x02') {
      dmAdvGenConnCmpl(0,0x3c);
    }
    else if (cVar2 != '\0') {
      *(char *)(param_1 + 2) = cVar2;
      (**(code **)(_DAT_004bac90 + 8))(param_1);
    }
  }
  return CONCAT44(param_2,iVar3);
}

