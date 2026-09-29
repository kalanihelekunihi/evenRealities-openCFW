
undefined4 FUN_0800c616(int *param_1,int param_2)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    FUN_0800bffc();
    param_1[2] = param_1[0x10] * param_1[0xf] + *param_1;
    param_1[0xe] = 0;
    param_1[1] = *param_1;
    param_1[3] = param_1[0x10] * (param_1[0xf] + -1) + *param_1;
    *(undefined1 *)(param_1 + 0x11) = 0xff;
    *(undefined1 *)((int)param_1 + 0x45) = 0xff;
    if (param_2 == 0) {
      if ((param_1[4] != 0) && (iVar1 = FUN_0800cba0(param_1 + 4), iVar1 != 0)) {
        FUN_0800c0a0();
      }
    }
    else {
      FUN_0800bf94();
      FUN_0800bf94(param_1 + 9);
    }
    FUN_0800c014();
    return 1;
  }
  disableIRQinterrupts();
  do {
                    /* WARNING: Do nothing block with infinite loop */
  } while( true );
}

