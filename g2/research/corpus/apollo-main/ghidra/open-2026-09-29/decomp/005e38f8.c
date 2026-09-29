
undefined8 smprActProcPairReq(int param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iStack_20;
  undefined *puStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iStack_20 = param_1;
  puStack_1c = param_2;
  uStack_18 = param_3;
  uStack_14 = param_4;
  if (*(int *)(param_1 + 0x30) == 0) {
    uVar1 = WsfBufAlloc(0x40);
    *(undefined4 *)(param_1 + 0x30) = uVar1;
    if (*(int *)(param_1 + 0x30) == 0) {
      param_2[3] = 8;
      param_2[2] = 3;
      smpSmExecute(param_1,param_2);
      goto LAB_005e3a76;
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_005e3bc8,&DAT_005e3bc8,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_005e3bc8,PTR_DAT_005e3d3c,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_005e3bc8,PTR_DAT_005e3d40,4), iVar2 != 0)) {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) ||
               (iVar2 = FUN_0044b610(&DAT_005e3bcc,&PTR_LAB_005e3d2c,3), iVar2 != 0)) {
              WsfTrace(&DAT_005e3bc8,PTR_s_pScr_already_allocated_005e3d30);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              puStack_1c = PTR_s_pScr_already_allocated_005e3d30;
              iStack_20 = 0x62;
              FUN_0043d574(4,&DAT_005e3bcc,PTR_s_D__01_workspace_s200_ap510b_iar__005e3d38,
                           PTR_s_smprActProcPairReq_005e3d34);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            puStack_1c = PTR_s_pScr_already_allocated_005e3d30;
            iStack_20 = 0x62;
            FUN_0043d574(3,&DAT_005e3bcc,PTR_s_D__01_workspace_s200_ap510b_iar__005e3d38,
                         PTR_s_smprActProcPairReq_005e3d34);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          puStack_1c = PTR_s_pScr_already_allocated_005e3d30;
          iStack_20 = 0x62;
          FUN_0043d574(2,&DAT_005e3bcc,PTR_s_D__01_workspace_s200_ap510b_iar__005e3d38,
                       PTR_s_smprActProcPairReq_005e3d34);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puStack_1c = PTR_s_pScr_already_allocated_005e3d30;
        iStack_20 = 0x62;
        FUN_0043d574(1,&DAT_005e3bcc,PTR_s_D__01_workspace_s200_ap510b_iar__005e3d38,
                     PTR_s_smprActProcPairReq_005e3d34);
      }
    }
  }
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,1);
  iVar2 = *(int *)(param_2 + 4);
  FUN_00439be4(param_1 + 0x20,iVar2 + 8,7);
  uStack_14 = CONCAT13(*(undefined1 *)(iVar2 + 0xe),
                       CONCAT12(*(undefined1 *)(iVar2 + 0xd),
                                CONCAT11(*(undefined1 *)(iVar2 + 10),*(undefined1 *)(iVar2 + 0xb))))
  ;
  uStack_18._0_3_ = CONCAT12(0x31,(ushort)*(byte *)(param_1 + 0x3d));
  DmSmpCbackExec(&uStack_18);
LAB_005e3a76:
  return CONCAT44(puStack_1c,iStack_20);
}

