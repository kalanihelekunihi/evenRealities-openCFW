
longlong stm32_hal_peripheral_init(int *param_1,undefined4 param_2,uint param_3)

{
  int iVar1;
  int iVar2;
  
  if ((char)param_1[10] == '\x01') {
    return CONCAT44(param_1,2);
  }
  *(undefined1 *)(param_1 + 10) = 1;
  *(undefined1 *)((int)param_1 + 0x29) = 2;
  *(undefined4 *)(*param_1 + 0x24) = 0xca;
  *(undefined4 *)(*param_1 + 0x24) = 0x53;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffbff;
  *(uint *)(*param_1 + 0x5c) = *(uint *)(*param_1 + 0x5c) | 4;
  if (-1 < *(int *)(DAT_08005a48 + 0xc) << 0x19) {
    iVar1 = case_tick_word2();
    while (-1 < *(int *)(*param_1 + 0xc) << 0x1d) {
      iVar2 = case_tick_word2();
      if (1000 < (uint)(iVar2 - iVar1)) {
        *(undefined4 *)(*param_1 + 0x24) = 0xff;
        *(undefined1 *)((int)param_1 + 0x29) = 3;
        *(undefined1 *)(param_1 + 10) = 0;
        return CONCAT44(param_1,3);
      }
    }
  }
  *(undefined4 *)(*param_1 + 0x14) = param_2;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) & 0xfffffff8;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | param_3;
  *DAT_08005a4c = *DAT_08005a4c | 0x80000;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | 0x4000;
  *(uint *)(*param_1 + 0x18) = *(uint *)(*param_1 + 0x18) | 0x400;
  *(undefined4 *)(*param_1 + 0x24) = 0xff;
  *(undefined1 *)((int)param_1 + 0x29) = 1;
  *(undefined1 *)(param_1 + 10) = 0;
  return ZEXT48(param_1) << 0x20;
}

