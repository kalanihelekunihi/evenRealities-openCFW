
longlong case_wait_controller_channels
                   (undefined4 *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  param_1[0x24] = 0;
  uVar1 = case_tick_word2();
  uVar3 = DAT_080086dc;
  if (*(int *)*param_1 << 0x1c < 0) {
    param_2 = DAT_080086dc;
    iVar2 = case_wait_condition(param_1,0x200000,0,uVar1,DAT_080086dc,uVar1,param_4);
    if (iVar2 != 0) goto LAB_080086c8;
  }
  if (*(int *)*param_1 << 0x1d < 0) {
    iVar2 = case_wait_condition(param_1,0x400000,0,uVar1,uVar3,uVar1,param_4);
    param_2 = uVar3;
    if (iVar2 != 0) {
LAB_080086c8:
      return CONCAT44(param_2,3);
    }
  }
  param_1[0x22] = 0x20;
  param_1[0x23] = 0x20;
  param_1[0x1b] = 0;
  param_1[0x1c] = 0;
  *(undefined1 *)(param_1 + 0x21) = 0;
  return (ulonglong)param_2 << 0x20;
}

