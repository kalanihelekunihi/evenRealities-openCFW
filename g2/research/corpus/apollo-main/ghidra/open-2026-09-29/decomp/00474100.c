
undefined4 FUN_00474100(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 in_r3;
  undefined4 local_30 [8];
  undefined4 local_10;
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  if (*DAT_004744a8 == 0) {
    iVar1 = FUN_00443484();
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x170,
                     DAT_00474514);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00474518);
      }
      uVar2 = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x174,
                     DAT_0047451c);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_00474520,DAT_00474520);
      }
      FUN_0043c0e4(local_30,0x24,0);
      iVar1 = DAT_004742f8;
      local_10 = 1;
      local_30[0] = 0;
      iVar3 = osMessageQueuePut(*(undefined4 *)(DAT_004742f8 + 0xc),local_30,0,1000);
      if (iVar3 == 0) {
        local_30[0] = 1;
        iVar3 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),local_30,0,1000);
        if (iVar3 == 0) {
          local_30[0] = 3;
          iVar1 = osMessageQueuePut(*(undefined4 *)(iVar1 + 0xc),local_30,0,1000);
          if (iVar1 == 0) {
            uVar2 = 0;
          }
          else {
            iVar1 = FUN_0043d0ce();
            if (iVar1 << 0x1e < 0) {
              FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x188,
                           DAT_004744fc);
            }
            iVar1 = FUN_0043d0ce();
            if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_00474504,DAT_00474504);
            }
            uVar2 = 0xffffffff;
          }
        }
        else {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x182,
                         DAT_00474524);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x8000000,DAT_00474528,DAT_00474528);
          }
          uVar2 = 0xffffffff;
        }
      }
      else {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(2,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x17c,
                       DAT_004744d8);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_004744e0,DAT_004744e0);
        }
        uVar2 = 0xffffffff;
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,PTR_s_task_displaydrvmgr_0047430c,DAT_00474308,DAT_0047450c,0x16a,DAT_00474508)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_00474510,DAT_00474510);
    }
    uVar2 = 0;
  }
  return uVar2;
}

