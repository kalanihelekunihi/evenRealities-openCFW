
undefined8 case_calibrate_controller(int *param_1)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint local_20;
  
  local_20 = 0;
  iVar6 = 0;
  if ((char)param_1[0x15] == '\x01') {
    return 2;
  }
  *(undefined1 *)(param_1 + 0x15) = 1;
  uVar1 = case_start_controller_flag0(param_1);
  iVar2 = case_status_word2_bit0_alias(*param_1);
  if (iVar2 == 0) {
    param_1[0x16] = param_1[0x16] & 0xfffffeffU | 2;
    iVar2 = *param_1;
    uVar3 = *(uint *)(iVar2 + 0xc) & DAT_080040ec;
    *(uint *)(iVar2 + 0xc) = *(uint *)(iVar2 + 0xc) & ~DAT_080040ec;
    uVar5 = 0;
    do {
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffe8 | 0x80000000;
      while (*(int *)(*param_1 + 8) < 0) {
        local_20 = local_20 + 1;
        if (DAT_080040f0 <= local_20) {
          param_1[0x16] = param_1[0x16] & 0xfffffffdU | 0x10;
          *(undefined1 *)(param_1 + 0x15) = 0;
          goto LAB_080040c2;
        }
      }
      uVar5 = uVar5 + 1;
      iVar6 = (*(uint *)(*param_1 + 0xb4) & 0x7f) + iVar6;
    } while (uVar5 < 8);
    uVar4 = __aeabi_uidiv(iVar6);
    uVar5 = DAT_080040f4;
    *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & DAT_080040f4) + 1;
    *(uint *)(*param_1 + 0xb4) = *(uint *)(*param_1 + 0xb4) & 0xffffff80 | uVar4;
    *(uint *)(*param_1 + 8) = (*(uint *)(*param_1 + 8) & uVar5) + 2;
    iVar6 = case_tick_word2();
    while (iVar2 = case_status_word2_bit0_alias(*param_1), iVar2 != 0) {
      iVar2 = case_tick_word2();
      if ((2 < (uint)(iVar2 - iVar6)) &&
         (iVar2 = case_status_word2_bit0_alias(*param_1), iVar2 != 0)) {
        param_1[0x16] = param_1[0x16] | 0x10;
        param_1[0x17] = param_1[0x17] | 1;
LAB_080040c2:
        return CONCAT44(local_20,1);
      }
    }
    *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) | uVar3;
    uVar3 = (param_1[0x16] & 0xfffffffcU) + 1;
  }
  else {
    uVar3 = param_1[0x16] | 0x10;
  }
  param_1[0x16] = uVar3;
  *(undefined1 *)(param_1 + 0x15) = 0;
  return CONCAT44(local_20,uVar1);
}

