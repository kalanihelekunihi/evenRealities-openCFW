
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 HUB_MessageProcesser(short *param_1,undefined4 param_2,undefined *param_3)

{
  short sVar1;
  short sVar2;
  int iVar3;
  uint uVar4;
  
  sVar2 = 0;
  sVar1 = *param_1;
  uVar4 = 0;
  do {
    if (7 < uVar4) {
      if (uVar4 == 8) {
        iVar3 = FUN_0043d0ce(sVar2);
        if (iVar3 << 0x1e < 0) {
          param_2 = 0xb7;
          param_3 = PTR_s__HUB_MessageProcesser_Receive_er_004a7350;
          FUN_0043d574(1,DAT_004a6ee0,DAT_004a6edc,PTR_s_HUB_MessageProcesser_004a7354,0xb7,
                       PTR_s__HUB_MessageProcesser_Receive_er_004a7350,sVar1);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,PTR_s__sensor_hub__HUB_MessageProcesse_004a7358,
                              PTR_s__sensor_hub__HUB_MessageProcesse_004a7358,sVar1);
        }
      }
LAB_004a696a:
      return CONCAT44(param_3,param_2);
    }
    sVar2 = sVar1;
    if ((sVar1 == *(short *)(_DAT_004a734c + uVar4 * 8)) &&
       (sVar2 = 0, *(int *)(_DAT_004a734c + uVar4 * 8 + 4) != 0)) {
      (**(code **)(_DAT_004a734c + uVar4 * 8 + 4))(param_1);
      goto LAB_004a696a;
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

