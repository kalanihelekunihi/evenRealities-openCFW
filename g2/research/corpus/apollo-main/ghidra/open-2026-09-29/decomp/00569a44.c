
void WsfAssert(int param_1,undefined2 param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(1,DAT_00569aec,DAT_00569ae8,DAT_00569ae4,0x2b,DAT_00569ae0,param_1,param_2);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x4800000,DAT_00569af0,DAT_00569af0,param_1,param_2);
  }
  if (param_1 == 0) {
    if (*DAT_00569af4 == 0) {
      FUN_0043d574(0,DAT_00569b00,DAT_00569ae8,DAT_00569ae4,0x2c,DAT_00569afc,DAT_00569af8,
                   DAT_00569ae4,0x2c);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_00569af4)(DAT_00569af8,DAT_00569ae4,0x2c);
  }
  do {
  } while ((char)uVar2 == '\0');
  return;
}

