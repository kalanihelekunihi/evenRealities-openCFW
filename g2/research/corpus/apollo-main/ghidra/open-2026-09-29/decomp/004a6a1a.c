
undefined8 HUB_SendMessage(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  if (((param_1 != 0) && (*(int *)(DAT_004a6ecc + 0xc) != 0)) &&
     (iVar1 = osMessageQueuePut(*(undefined4 *)(DAT_004a6ecc + 0xc),param_1,0,0,param_1,param_2,
                                param_3,param_4), iVar1 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xf2;
      param_2 = DAT_004a7370;
      FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,DAT_004a7374,0xf2,DAT_004a7370,iVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,PTR_s__sensor_hub__HUB_MessageProcesse_004a7378,
                          PTR_s__sensor_hub__HUB_MessageProcesse_004a7378,iVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

