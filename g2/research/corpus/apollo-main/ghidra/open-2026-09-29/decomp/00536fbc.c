
void l2cMasterRxSignalingPkt(undefined2 param_1,ushort param_2,int param_3)

{
  char cVar1;
  undefined1 uVar2;
  int iVar3;
  int iVar4;
  ushort uStack_24;
  ushort uStack_22;
  ushort uStack_20;
  ushort uStack_1e;
  undefined2 uStack_1c;
  undefined2 uStack_1a;
  
  cVar1 = *(char *)(param_3 + 8);
  uVar2 = *(undefined1 *)(param_3 + 9);
  iVar4 = (uint)*(byte *)(param_3 + 0xb) * 0x100 + (uint)*(byte *)(param_3 + 10);
  if ((((uint)param_2 == iVar4 + 4U) && (cVar1 == '\x12')) && (iVar4 == 8)) {
    uStack_24 = (ushort)*(byte *)(param_3 + 0xd) * 0x100 + (ushort)*(byte *)(param_3 + 0xc);
    uStack_22 = (ushort)*(byte *)(param_3 + 0xf) * 0x100 + (ushort)*(byte *)(param_3 + 0xe);
    uStack_20 = (ushort)*(byte *)(param_3 + 0x11) * 0x100 + (ushort)*(byte *)(param_3 + 0x10);
    uStack_1e = (ushort)*(byte *)(param_3 + 0x13) * 0x100 + (ushort)*(byte *)(param_3 + 0x12);
    uStack_1c = 0;
    uStack_1a = 0;
    if ((((uStack_24 - 6 < 0xc7b) && (uStack_24 <= uStack_22)) && (uStack_22 - 6 < 0xc7b)) &&
       ((uStack_20 < 500 && (uStack_1e - 10 < 0xc77)))) {
      DmL2cConnUpdateInd(uVar2,param_1,&uStack_24);
    }
    else {
      L2cDmConnUpdateRsp(uVar2,param_1,1);
    }
  }
  else {
    iVar3 = FUN_004c9c50();
    if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537214,s_apGERR_00537205 + 3,3), iVar3 != 0)
       ) {
      iVar3 = FUN_004c9c50();
      if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537214,PTR_DAT_00537214,4), iVar3 != 0)) {
        iVar3 = FUN_004c9c50();
        if ((iVar3 == 0) || (iVar3 = FUN_0044b610(PTR_DAT_00537214,PTR_DAT_00537224,4), iVar3 != 0))
        {
          iVar3 = FUN_004c9c50();
          if (iVar3 == 0) {
            iVar3 = FUN_004c9c50();
            if ((iVar3 == 0) ||
               (iVar3 = FUN_0044b610(&DAT_0053720c,&PTR_LAB_00537210,3), iVar3 != 0)) {
              WsfTrace(PTR_DAT_00537214,PTR_s_invalid_msg_code__d_len__d_l2cLe_00537218,cVar1,iVar4,
                       param_2);
            }
          }
          else {
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(4,&DAT_0053720c,PTR_s_D__01_workspace_s200_ap510b_iar__00537220,
                           PTR_s_l2cMasterRxSignalingPkt_0053721c,0x46,
                           PTR_s_invalid_msg_code__d_len__d_l2cLe_00537218,cVar1,iVar4,param_2);
            }
          }
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(3,&DAT_0053720c,PTR_s_D__01_workspace_s200_ap510b_iar__00537220,
                         PTR_s_l2cMasterRxSignalingPkt_0053721c,0x46,
                         PTR_s_invalid_msg_code__d_len__d_l2cLe_00537218,cVar1,iVar4,param_2);
          }
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,&DAT_0053720c,PTR_s_D__01_workspace_s200_ap510b_iar__00537220,
                       PTR_s_l2cMasterRxSignalingPkt_0053721c,0x46,
                       PTR_s_invalid_msg_code__d_len__d_l2cLe_00537218,cVar1,iVar4,param_2);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,&DAT_0053720c,PTR_s_D__01_workspace_s200_ap510b_iar__00537220,
                     PTR_s_l2cMasterRxSignalingPkt_0053721c,0x46,
                     PTR_s_invalid_msg_code__d_len__d_l2cLe_00537218,cVar1,iVar4,param_2);
      }
    }
    if (cVar1 != '\x01') {
      l2cSendCmdReject(param_1,uVar2,0);
    }
  }
  return;
}

