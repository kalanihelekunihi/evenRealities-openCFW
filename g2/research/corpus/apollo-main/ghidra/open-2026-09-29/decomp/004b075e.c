
undefined4 FUN_004b075e(int param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == 0) {
    param_1 = FUN_004c791a();
  }
  *(undefined4 *)(param_1 + 0x50) = 0;
  *(undefined1 *)(param_1 + 0x54) = 0xff;
  *(undefined1 *)(param_1 + 0x55) = 0xff;
  *(undefined1 *)(param_1 + 0x56) = 0xff;
  return unaff_r7;
}

