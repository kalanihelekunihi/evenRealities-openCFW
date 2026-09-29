
undefined8 FUN_08004480(int *param_1)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  bool bVar5;
  int local_20;
  
  local_20 = 0;
  if (param_1 == (int *)0x0) {
    return 1;
  }
  if (param_1[0x16] == 0) {
    case_configure_irq_resource(param_1);
    param_1[0x17] = 0;
    *(undefined1 *)(param_1 + 0x15) = 0;
  }
  iVar1 = *param_1;
  if (-1 < *(int *)(iVar1 + 8) << 3) {
    *(uint *)(iVar1 + 8) = *(uint *)(iVar1 + 8) & DAT_08004684 | 0x10000000;
    iVar1 = __aeabi_uidiv(*DAT_0800468c,DAT_08004688);
    for (local_20 = iVar1 * 2 + 2; local_20 != 0; local_20 = local_20 + -1) {
    }
  }
  bVar5 = -1 < *(int *)(*param_1 + 8) << 3;
  if (bVar5) {
    param_1[0x16] = param_1[0x16] | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
  }
  uVar4 = (uint)bVar5;
  iVar1 = case_status_word2_bit2();
  if ((param_1[0x16] << 0x1b < 0) || (iVar1 != 0)) {
    param_1[0x16] = param_1[0x16] | 0x10;
  }
  else {
    param_1[0x16] = param_1[0x16] & 0xfffffeffU | 2;
    iVar1 = case_status_word2_bit0(*param_1);
    if (iVar1 == 0) {
      uVar2 = 0;
      if (param_1[0xc] != 0) {
        uVar2 = 0x1000;
      }
      if (param_1[4] < 0) {
        uVar3 = param_1[4] & 0x7fffffff;
      }
      else {
        uVar3 = 0x200000;
      }
      uVar2 = param_1[2] | (uint)*(byte *)(param_1 + 6) << 0xe |
              (uint)*(byte *)((int)param_1 + 0x19) << 0xf |
              (uint)*(byte *)((int)param_1 + 0x1a) << 0xd | uVar2 | param_1[3] | uVar3 |
              (uint)*(byte *)(param_1 + 0xb) << 1;
      if ((char)param_1[8] == '\x01') {
        if (*(byte *)((int)param_1 + 0x1a) == 0) {
          uVar2 = uVar2 | 0x10000;
        }
        else {
          param_1[0x16] = param_1[0x16] | 0x20;
          param_1[0x17] = param_1[0x17] | 1;
        }
      }
      if (param_1[9] != 0) {
        uVar2 = param_1[10] | param_1[9] & 0x1c0U | uVar2;
      }
      *(uint *)(*param_1 + 0xc) = *(uint *)(*param_1 + 0xc) & DAT_08004690 | uVar2;
      uVar2 = DAT_08004694;
      uVar3 = param_1[0x13] | param_1[1] & 0xc0000000U;
      if ((char)param_1[0xf] == '\x01') {
        uVar3 = uVar3 | param_1[0x10] | param_1[0x11] |
                        param_1[0x12] | (param_1[1] & 0xc0000000U) + 1;
      }
      *(uint *)(*param_1 + 0x10) = *(uint *)(*param_1 + 0x10) & DAT_08004694 | uVar3;
      uVar3 = param_1[1];
      if (((uVar3 != 0xc0000000) && (uVar3 != uVar2 * 0x20000000)) && (uVar3 != uVar2 * 0x40000000))
      {
        *(uint *)(DAT_08004698 + 8) = *(uint *)(DAT_08004698 + 8) & 0xffc3ffff | uVar3 & 0x3c0000;
      }
    }
    case_control_word5_replace_slot(*param_1,0,param_1[0xd]);
    case_control_word5_replace_slot(*param_1,DAT_0800469c,param_1[0xe]);
    if (param_1[4] == 0) {
      *(uint *)(*param_1 + 0x28) = *(uint *)(*param_1 + 0x28) | 0xfffffff0;
    }
    else if (param_1[4] == 0x200000) {
      *(int *)(*param_1 + 0x28) = -0x10 << ((char)param_1[7] * '\x04' - 4U & 0x1f) | param_1[0x18];
    }
    if ((*(uint *)(*param_1 + 0x14) & 7) == param_1[0xd]) {
      param_1[0x17] = 0;
      param_1[0x16] = (param_1[0x16] & 0xfffffffcU) + 1;
      goto LAB_0800467e;
    }
    param_1[0x16] = param_1[0x16] & 0xfffffffdU | 0x10;
    param_1[0x17] = param_1[0x17] | 1;
  }
  uVar4 = 1;
LAB_0800467e:
  return CONCAT44(local_20,uVar4);
}

