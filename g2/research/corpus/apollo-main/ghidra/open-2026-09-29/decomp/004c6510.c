
undefined8 device_mgr_fn_004c6510(short *param_1,undefined4 param_2,undefined *param_3)

{
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  
  sVar2 = 0;
  sVar1 = *param_1;
  uVar4 = 0;
  do {
    if (4 < uVar4) {
      if (uVar4 == 5) {
        iVar3 = FUN_0043d0ce(sVar2);
        if (iVar3 << 0x1e < 0) {
          param_2 = 0xf8;
          param_3 = PTR_s__DEV_MessageProcesser_Receive_er_004c6c58;
          FUN_0043d574(1,DAT_004c6c00,DAT_004c6bfc,PTR_s_DEV_MessageProcesser_004c6c5c,0xf8,
                       PTR_s__DEV_MessageProcesser_Receive_er_004c6c58,sVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__device_mgr__DEV_MessageProcesse_004c6c60,
                              PTR_s__device_mgr__DEV_MessageProcesse_004c6c60,sVar1);
        }
      }
LAB_004c6598:
      return CONCAT44(param_3,param_2);
    }
    sVar2 = sVar1;
    if ((sVar1 == *(short *)(PTR_DAT_004c6c54 + uVar4 * 8)) &&
       (sVar2 = 0, *(int *)(PTR_DAT_004c6c54 + uVar4 * 8 + 4) != 0)) {
      (**(code **)(PTR_DAT_004c6c54 + uVar4 * 8 + 4))(param_1);
      goto LAB_004c6598;
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

