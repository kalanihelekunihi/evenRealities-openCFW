
void FUN_0800c2f8(int param_1)

{
  int *piVar1;
  
  FUN_0800bffc();
  piVar1 = DAT_0800c378;
  if (param_1 == 0) {
    param_1 = *DAT_0800c378;
  }
  uxListRemove(param_1 + 4);
  if (*(int *)(param_1 + 0x28) != 0) {
    uxListRemove(param_1 + 0x18);
  }
  FUN_0800bfe2(DAT_0800c37c,param_1 + 4);
  if (*(char *)(param_1 + 0x58) == '\x01') {
    *(undefined1 *)(param_1 + 0x58) = 0;
  }
  FUN_0800c014();
  if (piVar1[5] != 0) {
    FUN_0800bffc();
    FUN_0800b260();
    FUN_0800c014();
  }
  if (param_1 == *piVar1) {
    if (piVar1[5] == 0) {
      if (*DAT_0800c37c == piVar1[2]) {
        *piVar1 = 0;
        return;
      }
      vTaskSwitchContext();
      return;
    }
    if (piVar1[0xc] != 0) {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_0800c0a0();
  }
  return;
}

