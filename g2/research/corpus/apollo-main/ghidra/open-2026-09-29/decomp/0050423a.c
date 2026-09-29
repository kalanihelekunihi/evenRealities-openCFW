
undefined8 HAL_I2CInit(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  uVar5 = 0;
  uVar4 = 0;
  do {
    iVar2 = DAT_00504768;
    iVar3 = DAT_00504760;
    if (7 < uVar4) {
      FUN_0055c498(*(undefined4 *)(DAT_00504760 + 0x44),0xff);
      hal_i2c_irq_enable(10);
      piVar1 = DAT_0050476c;
      iVar3 = osSemaphoreNew(1,0,0);
      *piVar1 = iVar3;
      if (*piVar1 == 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          param_3 = 0x131;
          FUN_0043d574(1,DAT_0050477c,DAT_00504778,DAT_00504774,0x131,DAT_00504770);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_00504780,DAT_00504780);
        }
        uVar5 = 1;
      }
LAB_0050436c:
      return CONCAT44(param_3,uVar5);
    }
    if ((*(int *)(uVar4 * 0x10 + DAT_00504760 + 8) != 0) &&
       (*(int *)(uVar4 * 0x10 + DAT_00504760 + 0xc) != 0)) {
      if (*(int *)(DAT_00504768 + uVar4 * 4) == 0) {
        uVar5 = osMutexNew(0);
        *(undefined4 *)(iVar2 + uVar4 * 4) = uVar5;
        if (*(int *)(iVar2 + uVar4 * 4) == 0) {
          uVar5 = 1;
          goto LAB_0050436c;
        }
      }
      FUN_0055c2bc(*(undefined4 *)(iVar3 + uVar4 * 0x10),uVar4 * 0x10 + iVar3 + 4);
      iVar2 = FUN_00480f0c(**(undefined4 **)(uVar4 * 0x10 + iVar3 + 8),
                           *(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 8));
      if (iVar2 != 0) {
        uVar5 = 1;
        goto LAB_0050436c;
      }
      iVar2 = FUN_00480f0c(*(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 4),
                           *(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 0xc));
      if (iVar2 != 0) {
        uVar5 = 1;
        goto LAB_0050436c;
      }
      FUN_0055c7e8(*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4),0,0);
      FUN_0055ca94(*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4),
                   *(undefined4 *)(uVar4 * 0x10 + iVar3 + 0xc));
      uVar5 = FUN_0055c32e(*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4));
      hal_i2c_power_up(uVar4 & 0xff);
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

