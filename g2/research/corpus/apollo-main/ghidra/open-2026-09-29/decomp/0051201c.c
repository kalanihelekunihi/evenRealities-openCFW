
void FUN_0051201c(undefined4 param_1)

{
  char *pcVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  float fVar5;
  float fVar6;
  char local_2c;
  byte local_2b [3];
  float local_28;
  float local_24;
  float local_20 [2];
  
  uVar2 = FUN_0055ee8c(DAT_00512384,0);
  iVar3 = FUN_00511990(local_20,&local_24,&local_28,&local_2c);
  iVar4 = DAT_00512388;
  if (iVar3 == DAT_00512388) {
    iVar3 = FUN_0055ef3c(uVar2,local_2b);
    if (iVar3 == iVar4) {
      if ((int)((uint)local_2b[0] << 0x1f) < 0) {
        iVar4 = FUN_0055f74c(0,0);
      }
      else {
        iVar4 = FUN_0055f74c(1,0);
      }
      if (iVar4 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512834,0x31c,DAT_0051260c,iVar4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_00512610,DAT_00512610,iVar4);
        }
      }
      fVar5 = (float)FUN_0055f848(local_20[0],local_24,local_28,param_1,0);
      FUN_0055f994();
      FUN_0055f9a0();
      fVar6 = DAT_005122d0;
      if (((-1 < (int)((uint)(fVar5 < 0.0) << 0x1f)) && (fVar5 < DAT_005122cc)) &&
         (fVar6 = fVar5, DAT_005122d4 <= fVar5)) {
        fVar6 = DAT_005122d4;
      }
      if ((((DAT_005122d8 <= fVar6) && ((int)((uint)(fVar6 < DAT_005122dc) << 0x1f) < 0)) ||
          ((DAT_005122e0 <= fVar6 && ((int)((uint)(fVar6 < DAT_00512374) << 0x1f) < 0)))) ||
         ((DAT_00512378 <= fVar6 && ((int)((uint)(fVar6 < DAT_0051237c) << 0x1f) < 0)))) {
        *(undefined1 *)(DAT_00512608 + 0x15) = 1;
      }
      else {
        *(undefined1 *)(DAT_00512608 + 0x15) = 0;
      }
      iVar4 = DAT_00512608;
      *(int *)(DAT_00512608 + 4) = (int)fVar6;
      fVar6 = DAT_00512380;
      *(int *)(iVar4 + 8) = (int)(local_20[0] * DAT_00512380);
      *(int *)(iVar4 + 0xc) = (int)(local_24 * fVar6);
      *(int *)(iVar4 + 0x10) = (int)(local_28 * DAT_005122d4);
      pcVar1 = DAT_005128f4;
      if ((local_2c != *DAT_005128f4) && (iVar4 = FUN_00511b74(local_2c), iVar4 != 0)) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512834,0x374,DAT_00512618,iVar4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0051261c,DAT_0051261c,iVar4);
        }
      }
      *pcVar1 = local_2c;
    }
    else {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00512408,DAT_00512404,DAT_00512834,0x312,DAT_00512830,iVar3);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00512838,DAT_00512838,iVar3);
      }
    }
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00512408,DAT_00512404,DAT_00512834,0x30c,DAT_00512594,iVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8400000,PTR_s__npmx_driver_ERROR__npmx_get_adc_00512598,
                          PTR_s__npmx_driver_ERROR__npmx_get_adc_00512598,iVar3);
    }
  }
  return;
}

