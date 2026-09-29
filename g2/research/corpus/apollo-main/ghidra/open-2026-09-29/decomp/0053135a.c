
undefined8 attcConnCback(int param_1,undefined *param_2)

{
  char cVar1;
  ushort uVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  byte bVar6;
  int iVar7;
  
  iVar4 = DAT_00531bac;
  iVar7 = param_1;
  if (param_2[2] == '\'') {
    iVar4 = DmConnRole(*(undefined1 *)(param_1 + 0xe));
    if (iVar4 == 0) {
      uVar2 = HciGetMaxRxAclLen();
      if ((int)(uint)*(ushort *)(*DAT_00531aac + 4) < (int)(uVar2 - 4)) {
        sVar3 = *(short *)(*DAT_00531aac + 4);
      }
      else {
        sVar3 = HciGetMaxRxAclLen();
        sVar3 = sVar3 + -4;
      }
      if (sVar3 != 0xf7) {
        AttcMtuReq(*(undefined1 *)(param_1 + 0xe),sVar3);
      }
    }
  }
  else if (param_2[2] == '(') {
    if (param_2[3] == '\0') {
      cVar1 = param_2[8];
    }
    else {
      cVar1 = param_2[3];
    }
    if (*(char *)((uint)*(byte *)(param_1 + 0xe) * 0xc + DAT_00531bac + 0x182) != '\0') {
      attcReqClear(*(undefined1 *)(param_1 + 0xe),
                   DAT_00531bac + (uint)*(byte *)(param_1 + 0xe) * 0xc + 0x180,cVar1 + -0x60);
    }
    for (bVar6 = 0; bVar6 < 3; bVar6 = bVar6 + 1) {
      if (*(char *)(param_1 + 0xe) == '\0') {
        iVar4 = FUN_004c9c50();
        if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00531b90,&DAT_005315ac,3), iVar4 != 0)) {
          iVar4 = FUN_004c9c50();
          if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00531b90,DAT_00531b90,4), iVar4 != 0)) {
            iVar4 = FUN_004c9c50();
            if ((iVar4 == 0) || (iVar4 = FUN_0044b610(DAT_00531b90,DAT_00531b18,4), iVar4 != 0)) {
              iVar4 = FUN_004c9c50();
              if (iVar4 == 0) {
                iVar4 = FUN_004c9c50();
                if ((iVar4 == 0) ||
                   (iVar4 = FUN_0044b610(&DAT_005315b0,&DAT_005315a8,3), iVar4 != 0)) {
                  WsfTrace(DAT_00531b90,PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0,
                           *(undefined1 *)(param_1 + 0xe));
                }
              }
              else {
                iVar4 = FUN_0043d0ce();
                if (iVar4 << 0x1e < 0) {
                  iVar7 = 0x262;
                  param_2 = PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0;
                  FUN_0043d574(4,&DAT_005315b0,DAT_00531abc,PTR_s_attcConnCback_00531bb4,0x262,
                               PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0,
                               *(undefined1 *)(param_1 + 0xe));
                }
              }
            }
            else {
              iVar4 = FUN_0043d0ce();
              if (iVar4 << 0x1e < 0) {
                iVar7 = 0x262;
                param_2 = PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0;
                FUN_0043d574(3,&DAT_005315b0,DAT_00531abc,PTR_s_attcConnCback_00531bb4,0x262,
                             PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0,
                             *(undefined1 *)(param_1 + 0xe));
              }
            }
          }
          else {
            iVar4 = FUN_0043d0ce();
            if (iVar4 << 0x1e < 0) {
              iVar7 = 0x262;
              param_2 = PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0;
              FUN_0043d574(2,&DAT_005315b0,DAT_00531abc,PTR_s_attcConnCback_00531bb4,0x262,
                           PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0,
                           *(undefined1 *)(param_1 + 0xe));
            }
          }
        }
        else {
          iVar4 = FUN_0043d0ce();
          if (iVar4 << 0x1e < 0) {
            iVar7 = 0x262;
            param_2 = PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0;
            FUN_0043d574(1,&DAT_005315b0,DAT_00531abc,PTR_s_attcConnCback_00531bb4,0x262,
                         PTR_s_Invalid_pCcb_>connId_in_attcReqC_00531bb0,
                         *(undefined1 *)(param_1 + 0xe));
          }
        }
        break;
      }
      iVar5 = (uint)*(byte *)(param_1 + 0xe) * 0x84 + iVar4 + (uint)bVar6 * 0x2c;
      if (*(char *)(iVar5 + -0x7e) != '\0') {
        WsfTimerStop(iVar5 + -0x6c);
        attcReqClear(*(undefined1 *)(iVar5 + -0x5b),iVar5 + -0x80,cVar1 + -0x60);
      }
      *(byte *)(param_1 + (uint)bVar6 * 4 + 2) = *(byte *)(param_1 + (uint)bVar6 * 4 + 2) & 0xfd;
      *(byte *)(param_1 + (uint)bVar6 * 4 + 2) = *(byte *)(param_1 + (uint)bVar6 * 4 + 2) & 0xef;
      if (*(int *)(iVar4 + 0x1b0) != 0) {
        (**(code **)(*(int *)(iVar4 + 0x1b0) + 4))(iVar5 + -0x84,cVar1 + -0x60);
      }
      attcWriteCmdCallback(*(undefined1 *)(param_1 + 0xe),iVar5 + -0x84,cVar1 + -0x60);
    }
  }
  return CONCAT44(param_2,iVar7);
}

