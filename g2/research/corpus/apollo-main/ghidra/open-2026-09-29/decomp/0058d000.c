
undefined8 FUN_0058d000(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  byte bVar2;
  byte bVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  uint *puVar7;
  
  if (param_2 == (uint *)0x0) {
    iVar4 = FUN_0043d0ce();
    puVar7 = param_2;
    if (iVar4 << 0x1e < 0) {
      puVar7 = (uint *)0x127;
      FUN_0043d574(1,DAT_0058d2dc,DAT_0058d2d8,PTR_s_teleprompt_action_page_data_0058d4b4,0x127,
                   PTR_s_page_data_is_NULL_0058d4b0,param_4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,PTR_s__teleprompt_fsm_page_data_is_NUL_0058d4b8);
    }
    uVar5 = 0xffffffff;
  }
  else {
    puVar7 = param_2;
    teleprompt_page_data_update(param_2);
    uVar6 = *param_2;
    iVar4 = FUN_005540b2();
    if ((((iVar4 == 2) && (*(int *)(DAT_0058d4bc + 0x18) != 0)) &&
        (*(char *)(DAT_0058d4bc + 0x21) == '\0')) && (*(int *)(DAT_0058d4bc + 0x3c) == 0)) {
      bVar3 = 1;
    }
    else {
      bVar3 = 0;
    }
    if ((*(char *)(param_1 + 0x3d) == '\0') || (*(uint *)(param_1 + 0x40) != uVar6)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if (((*(uint *)(param_1 + 0x10) == 0) || (*(uint *)(param_1 + 0x10) <= uVar6)) ||
       ((uVar6 < *(uint *)(DAT_0058d4bc + 0x2c) || (*(uint *)(DAT_0058d4bc + 0x2c) + 4 <= uVar6))))
    {
      bVar2 = 0;
    }
    else {
      bVar2 = 1;
    }
    if ((bool)(bVar3 & (bVar2 | bVar1))) {
      if (bVar1) {
        FUN_0058c882();
      }
      FUN_00589b68(6,uVar6);
    }
    uVar5 = 0;
  }
  return CONCAT44(puVar7,uVar5);
}

