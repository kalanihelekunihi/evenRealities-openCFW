
undefined8
task_vote_init(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = DAT_0046d878;
  FUN_0043c0e4(DAT_0046d878,0x108,0);
  *(undefined1 *)(iVar1 + 0x104) = 1;
  *(undefined4 *)(iVar1 + 0x100) = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_2 = 0x84;
    param_3 = DAT_0046d87c;
    FUN_0043d574(3,DAT_0046d888,DAT_0046d884,DAT_0046d880,0x84,DAT_0046d87c,param_4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0046d88c);
  }
  return CONCAT44(param_3,param_2);
}

