
undefined4 enter_dfu_mailbox_and_reset(uint param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 extraout_r1;
  undefined4 extraout_r2;
  int extraout_r3;
  
  if (1 < param_1) {
    software_bkpt(1);
  }
  *puRam00007e40 = (char)param_1;
  NVIC_SystemReset();
  iVar1 = (*(code *)(*(undefined4 **)(extraout_r3 + 0x1c))[5])
                    (**(undefined4 **)(extraout_r3 + 0x1c),*(undefined4 *)(extraout_r3 + 0x10),
                     extraout_r2,extraout_r1);
  uVar2 = 0;
  if (iVar1 != 0) {
    uVar2 = DAT_00007e64;
  }
  return uVar2;
}

