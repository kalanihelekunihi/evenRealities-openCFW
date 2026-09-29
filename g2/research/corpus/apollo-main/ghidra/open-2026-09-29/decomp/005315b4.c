
void attcMsgCback(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b18,&DAT_00531818,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b18,DAT_00531b90,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(DAT_00531b18,DAT_00531b18,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_005318f8,&DAT_0053181c,3), iVar1 != 0)) {
            WsfTrace(DAT_00531b18,PTR_s_attcMsgCback__msg____x_slot____x_00531bb8,
                     *(undefined1 *)((int)param_1 + 2),*(undefined1 *)((int)param_1 + 10));
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,&DAT_005318f8,DAT_00531abc,PTR_s_attcMsgCback_00531bbc,0x28b,
                         PTR_s_attcMsgCback__msg____x_slot____x_00531bb8,
                         *(undefined1 *)((int)param_1 + 2),*(undefined1 *)((int)param_1 + 10));
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(3,&DAT_005318f8,DAT_00531abc,PTR_s_attcMsgCback_00531bbc,0x28b,
                       PTR_s_attcMsgCback__msg____x_slot____x_00531bb8,
                       *(undefined1 *)((int)param_1 + 2),*(undefined1 *)((int)param_1 + 10));
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,&DAT_005318f8,DAT_00531abc,PTR_s_attcMsgCback_00531bbc,0x28b,
                     PTR_s_attcMsgCback__msg____x_slot____x_00531bb8,
                     *(undefined1 *)((int)param_1 + 2),*(undefined1 *)((int)param_1 + 10));
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,&DAT_005318f8,DAT_00531abc,PTR_s_attcMsgCback_00531bbc,0x28b,
                   PTR_s_attcMsgCback__msg____x_slot____x_00531bb8,*(undefined1 *)((int)param_1 + 2)
                   ,*(undefined1 *)((int)param_1 + 10),param_4);
    }
  }
  if (*(byte *)((int)param_1 + 2) - 0x11 < 2) {
    if (*(int *)(DAT_00531bac + 0x1b0) != 0) {
      (*(code *)**(undefined4 **)(DAT_00531bac + 0x1b0))(0,param_1);
    }
  }
  else {
    iVar1 = attcCcbByConnId((char)*(undefined2 *)param_1,*(undefined1 *)((int)param_1 + 10));
    if (iVar1 == 0) {
      if ((*(char *)((int)param_1 + 2) != '\0') && (*(byte *)((int)param_1 + 2) < 0x12)) {
        attcFreePkt(param_1);
      }
    }
    else if (*(byte *)((int)param_1 + 2) < 0x11) {
      if ((((*(char *)(iVar1 + 0x28) == '\0') &&
           (*(char *)(DAT_00531bac + (uint)*(byte *)(iVar1 + 0x29) * 0xc + 0x182) != '\0')) ||
          (1 < *(byte *)(iVar1 + 6))) ||
         ((*(char *)((int)param_1 + 2) == '\n' &&
          (iVar2 = attcPendWriteCmd(iVar1,*(undefined2 *)(param_1 + 2)), iVar2 != 0)))) {
        attcReqClear(*(undefined1 *)(iVar1 + 0x29),param_1,0x72);
      }
      else if ((*(char *)(iVar1 + 0x28) == '\0') && (*(char *)(iVar1 + 6) == '\x01')) {
        iVar1 = DAT_00531bac + (uint)*(byte *)(iVar1 + 0x29) * 0xc;
        uVar3 = param_1[1];
        uVar4 = param_1[2];
        *(undefined4 *)(iVar1 + 0x180) = *param_1;
        *(undefined4 *)(iVar1 + 0x184) = uVar3;
        *(undefined4 *)(iVar1 + 0x188) = uVar4;
      }
      else {
        attcSetupReq(iVar1,param_1);
      }
    }
    else if (*(char *)((int)param_1 + 2) == '\x13') {
      if ((*(char *)(iVar1 + 6) == '\0') || (*(char *)(iVar1 + 6) == '\x01')) {
        if ((*(char *)(iVar1 + 0x28) == '\0') &&
           (*(char *)((uint)*(byte *)(iVar1 + 0x29) * 0xc + DAT_00531bac + 0x182) != '\0')) {
          attcReqClear(*(undefined1 *)(iVar1 + 0x29),
                       DAT_00531bac + (uint)*(byte *)(iVar1 + 0x29) * 0xc + 0x180,0x74);
        }
      }
      else {
        WsfTimerStop(iVar1 + 0x18);
        attcReqClear(*(undefined1 *)(iVar1 + 0x29),iVar1 + 4,0x74);
      }
    }
  }
  return;
}

