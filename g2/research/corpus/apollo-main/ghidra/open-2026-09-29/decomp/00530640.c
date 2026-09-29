
undefined8
l2cDefaultDataCidCback(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined *puVar2;
  
  puVar2 = param_2;
  iVar1 = FUN_004c9c50();
  if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00530b74,&DAT_00530760,3), iVar1 != 0)) {
    iVar1 = FUN_004c9c50();
    if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b74,4), iVar1 != 0)) {
      iVar1 = FUN_004c9c50();
      if ((iVar1 == 0) || (iVar1 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b84,4), iVar1 != 0)) {
        iVar1 = FUN_004c9c50();
        if (iVar1 == 0) {
          iVar1 = FUN_004c9c50();
          if ((iVar1 == 0) || (iVar1 = FUN_0044b610(&DAT_00530764,&DAT_00530768,3), iVar1 != 0)) {
            WsfTrace(PTR_DAT_00530b74,PTR_s_unknown_cid_0x_04x_00530b88,(uint)param_2 & 0xffff);
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            param_1 = 0x4b;
            puVar2 = PTR_s_unknown_cid_0x_04x_00530b88;
            FUN_0043d574(4,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                         PTR_s_l2cDefaultDataCidCback_00530b8c,0x4b,
                         PTR_s_unknown_cid_0x_04x_00530b88,(uint)param_2 & 0xffff);
          }
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_1 = 0x4b;
          puVar2 = PTR_s_unknown_cid_0x_04x_00530b88;
          FUN_0043d574(3,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                       PTR_s_l2cDefaultDataCidCback_00530b8c,0x4b,PTR_s_unknown_cid_0x_04x_00530b88,
                       (uint)param_2 & 0xffff);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_1 = 0x4b;
        puVar2 = PTR_s_unknown_cid_0x_04x_00530b88;
        FUN_0043d574(2,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                     PTR_s_l2cDefaultDataCidCback_00530b8c,0x4b,PTR_s_unknown_cid_0x_04x_00530b88,
                     (uint)param_2 & 0xffff);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x4b;
      puVar2 = PTR_s_unknown_cid_0x_04x_00530b88;
      FUN_0043d574(1,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                   PTR_s_l2cDefaultDataCidCback_00530b8c,0x4b,PTR_s_unknown_cid_0x_04x_00530b88,
                   (uint)param_2 & 0xffff,param_4);
    }
  }
  return CONCAT44(puVar2,param_1);
}

