
undefined8 AttcIndConfirm(uint param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  uint uVar3;
  
  if ((param_1 & 0xff) == 0) {
    uVar3 = param_1;
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_LAB_004b59ac,&DAT_004b598c,3), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_LAB_004b59ac,PTR_LAB_004b59ac,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_LAB_004b59ac,PTR_LAB_004b59bc,4), iVar1 != 0))
        {
          iVar1 = FUN_004c9c50();
          if (iVar1 == 0) {
            iVar1 = FUN_004c9c50();
            if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_004b5990,&DAT_004b5994,3), iVar1 != 0)) {
              WsfTrace(PTR_LAB_004b59ac,PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0,
                       param_1 & 0xff);
            }
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              uVar3 = 0x31a;
              param_2 = PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0;
              FUN_0043d574(4,&DAT_004b5990,PTR_s_D__01_workspace_s200_ap510b_iar__004b59b8,
                           PTR_s_AttcIndConfirm_004b59b4,0x31a,
                           PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0,param_1 & 0xff);
            }
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar3 = 0x31a;
            param_2 = PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0;
            FUN_0043d574(3,&DAT_004b5990,PTR_s_D__01_workspace_s200_ap510b_iar__004b59b8,
                         PTR_s_AttcIndConfirm_004b59b4,0x31a,
                         PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0,param_1 & 0xff);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 0x31a;
          param_2 = PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0;
          FUN_0043d574(2,&DAT_004b5990,PTR_s_D__01_workspace_s200_ap510b_iar__004b59b8,
                       PTR_s_AttcIndConfirm_004b59b4,0x31a,
                       PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0,param_1 & 0xff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x31a;
        param_2 = PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0;
        FUN_0043d574(1,&DAT_004b5990,PTR_s_D__01_workspace_s200_ap510b_iar__004b59b8,
                     PTR_s_AttcIndConfirm_004b59b4,0x31a,
                     PTR_s_Invalid_connId_in_attcProcIndCon_004b59b0,param_1 & 0xff,param_4);
      }
    }
  }
  else {
    piVar2 = (int *)attcCcbByHandle((param_1 & 0xff) - 1 & 0xffff,0);
    uVar3 = param_1;
    if (((piVar2 != (int *)0x0) && ((*(byte *)(*piVar2 + 2) & 0x12) == 0x10)) &&
       (iVar1 = attMsgAlloc(9), uVar3 = param_1, iVar1 != 0)) {
      *(byte *)(*piVar2 + 2) = *(byte *)(*piVar2 + 2) & 0xef;
      *(undefined1 *)(iVar1 + 8) = 0x1e;
      L2cDataReq(4,*(undefined2 *)(*piVar2 + 0xc),1);
      uVar3 = param_1;
    }
  }
  return CONCAT44(param_2,uVar3);
}

