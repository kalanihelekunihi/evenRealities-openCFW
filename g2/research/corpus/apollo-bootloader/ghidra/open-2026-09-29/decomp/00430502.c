
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 platform_finish_430502(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  undefined4 uVar5;
  
  uVar5 = 0;
  uVar4 = 0;
  do {
    iVar2 = _DAT_00430648;
    iVar3 = DAT_00430640;
    if (7 < uVar4) {
      hw_interrupt_enable_42c63a(*(undefined4 *)(DAT_00430640 + 0x44),0xff);
      nvic_enable_bit_430470(10);
      piVar1 = _DAT_0043064c;
      iVar3 = bl_runtime_semaphore_create(1,0,0);
      *piVar1 = iVar3;
      if (*piVar1 == 0) {
        param_3 = 0x131;
        elog_output(1,PTR_s_hal_i2c_0043065c,PTR_s_D__01_workspace_s200_ap510b_iar__00430658,
                    PTR_s_HAL_I2CInit_00430654,0x131,PTR_s_Error___Failed_to_create_semapho_00430650
                   );
        uVar5 = 1;
      }
LAB_0043060e:
      return CONCAT44(param_3,uVar5);
    }
    if ((*(int *)(uVar4 * 0x10 + DAT_00430640 + 8) != 0) &&
       (*(int *)(uVar4 * 0x10 + DAT_00430640 + 0xc) != 0)) {
      if (*(int *)(_DAT_00430648 + uVar4 * 4) == 0) {
        uVar5 = bl_runtime_flags_create(0);
        *(undefined4 *)(iVar2 + uVar4 * 4) = uVar5;
        if (*(int *)(iVar2 + uVar4 * 4) == 0) {
          uVar5 = 1;
          goto LAB_0043060e;
        }
      }
      hw_context_claim_42c4c6(*(undefined4 *)(iVar3 + uVar4 * 0x10),uVar4 * 0x10 + iVar3 + 4);
      iVar2 = FUN_0041d92c(**(undefined4 **)(uVar4 * 0x10 + iVar3 + 8),
                           *(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 8));
      if (iVar2 != 0) {
        uVar5 = 1;
        goto LAB_0043060e;
      }
      iVar2 = FUN_0041d92c(*(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 4),
                           *(undefined4 *)(*(int *)(uVar4 * 0x10 + iVar3 + 8) + 0xc));
      if (iVar2 != 0) {
        uVar5 = 1;
        goto LAB_0043060e;
      }
      hw_config_transaction_42c988(*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4),0,0);
      hw_instance_configure_42cc34
                (*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4),
                 *(undefined4 *)(uVar4 * 0x10 + iVar3 + 0xc));
      uVar5 = hw_context_enable_42c538(*(undefined4 *)(uVar4 * 0x10 + iVar3 + 4));
      hw_config_retry_43048e(uVar4 & 0xff);
    }
    uVar4 = uVar4 + 1;
  } while( true );
}

