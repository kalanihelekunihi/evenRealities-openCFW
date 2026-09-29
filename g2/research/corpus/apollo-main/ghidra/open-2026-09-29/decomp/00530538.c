
undefined8 l2cDefaultDataCback(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_004c9c50();
  if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,&DAT_00530760,3), iVar2 != 0)) {
    iVar2 = FUN_004c9c50();
    if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b74,4), iVar2 != 0)) {
      iVar2 = FUN_004c9c50();
      if ((iVar2 == 0) || (iVar2 = FUN_0044b610(PTR_DAT_00530b74,PTR_DAT_00530b84,4), iVar2 != 0)) {
        iVar2 = FUN_004c9c50();
        if (iVar2 == 0) {
          iVar2 = FUN_004c9c50();
          if ((iVar2 == 0) || (iVar2 = FUN_0044b610(&DAT_00530764,&DAT_00530768,3), iVar2 != 0)) {
            WsfTrace(PTR_DAT_00530b74,PTR_s_rcvd_data_on_uregistered_cid_00530b78);
          }
        }
        else {
          iVar2 = FUN_0043d0ce();
          puVar1 = PTR_s_rcvd_data_on_uregistered_cid_00530b78;
          if (iVar2 << 0x1e < 0) {
            unaff_r5 = 0x3a;
            FUN_0043d574(4,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                         PTR_s_l2cDefaultDataCback_00530b7c);
            unaff_r6 = puVar1;
          }
        }
      }
      else {
        iVar2 = FUN_0043d0ce();
        puVar1 = PTR_s_rcvd_data_on_uregistered_cid_00530b78;
        if (iVar2 << 0x1e < 0) {
          unaff_r5 = 0x3a;
          FUN_0043d574(3,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                       PTR_s_l2cDefaultDataCback_00530b7c);
          unaff_r6 = puVar1;
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      puVar1 = PTR_s_rcvd_data_on_uregistered_cid_00530b78;
      if (iVar2 << 0x1e < 0) {
        unaff_r5 = 0x3a;
        FUN_0043d574(2,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                     PTR_s_l2cDefaultDataCback_00530b7c);
        unaff_r6 = puVar1;
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_rcvd_data_on_uregistered_cid_00530b78;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x3a;
      FUN_0043d574(1,&DAT_00530764,PTR_s_D__01_workspace_s200_ap510b_iar__00530b80,
                   PTR_s_l2cDefaultDataCback_00530b7c);
      unaff_r6 = puVar1;
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

