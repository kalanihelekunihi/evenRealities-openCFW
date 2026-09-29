
undefined8 l2cHciAclCback(byte *param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  byte *pbVar3;
  uint uVar4;
  int iVar5;
  byte *pbVar6;
  
  uVar1 = (uint)param_1[1] * 0x100 + (uint)*param_1 & 0xfff;
  uVar4 = (uint)param_1[3] * 0x100 + (uint)param_1[2];
  pbVar3 = param_1 + 4;
  if (uVar4 < 4) {
    iVar5 = 0;
  }
  else {
    iVar5 = (uint)param_1[5] * 0x100 + (uint)*pbVar3;
    pbVar3 = param_1 + 6;
  }
  pbVar6 = param_1;
  if (uVar4 == iVar5 + 4U) {
    uVar4 = (uint)pbVar3[1] * 0x100 + (uint)*pbVar3;
    if (uVar4 == 4) {
      (*(code *)*DAT_00530b90)(uVar1,iVar5,param_1);
    }
    else {
      if (3 < uVar4) {
        if (uVar4 == 6) {
          (*(code *)DAT_00530b90[1])(uVar1,iVar5,param_1);
          goto LAB_00530a94;
        }
        if (uVar4 < 6) {
          (*(code *)DAT_00530b90[2])(uVar1,iVar5,param_1);
          goto LAB_00530a94;
        }
      }
      (*(code *)DAT_00530b90[8])(uVar1,uVar4,iVar5,param_1,param_1,param_2,param_3,param_4);
    }
  }
  else {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,&DAT_00530a9c,3), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b74,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b84,4), iVar2 != 0))
        {
          iVar2 = FUN_004c9c50();
          if (iVar2 == 0) {
            iVar2 = FUN_004c9c50();
            if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530aa0,&DAT_00530adc,3), iVar2 != 0)) {
              WsfTrace(PTR_DAT_00530b74,PTR_s_length_mismatch__l2c__u_hci__u_00530b9c,iVar5,uVar4);
            }
          }
          else {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              pbVar6 = (byte *)0xc0;
              param_2 = PTR_s_length_mismatch__l2c__u_hci__u_00530b9c;
              FUN_0043d574(4,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                           PTR_s_l2cHciAclCback_00530ba0,0xc0,
                           PTR_s_length_mismatch__l2c__u_hci__u_00530b9c,iVar5,uVar4);
            }
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            pbVar6 = (byte *)0xc0;
            param_2 = PTR_s_length_mismatch__l2c__u_hci__u_00530b9c;
            FUN_0043d574(3,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                         PTR_s_l2cHciAclCback_00530ba0,0xc0,
                         PTR_s_length_mismatch__l2c__u_hci__u_00530b9c,iVar5,uVar4);
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          pbVar6 = (byte *)0xc0;
          param_2 = PTR_s_length_mismatch__l2c__u_hci__u_00530b9c;
          FUN_0043d574(2,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                       PTR_s_l2cHciAclCback_00530ba0,0xc0,
                       PTR_s_length_mismatch__l2c__u_hci__u_00530b9c,iVar5,uVar4);
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        pbVar6 = (byte *)0xc0;
        param_2 = PTR_s_length_mismatch__l2c__u_hci__u_00530b9c;
        FUN_0043d574(1,&DAT_00530aa0,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                     PTR_s_l2cHciAclCback_00530ba0,0xc0,
                     PTR_s_length_mismatch__l2c__u_hci__u_00530b9c,iVar5,uVar4);
      }
    }
  }
LAB_00530a94:
  WsfMsgFree(param_1);
  return CONCAT44(param_2,pbVar6);
}

