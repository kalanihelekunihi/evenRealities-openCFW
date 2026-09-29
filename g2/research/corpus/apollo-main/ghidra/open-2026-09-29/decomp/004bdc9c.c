
undefined4
APP_EvenOtaWriteCback
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
          undefined2 param_5,undefined4 param_6)

{
  char cVar1;
  int iVar2;
  
  cVar1 = FUN_0048d8d8(param_6,param_5,0,param_4,param_1,param_2,param_3,param_4);
  if (cVar1 != '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004bde0c,DAT_004bde08,DAT_004bde2c,0xbd,DAT_004bde28,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004bde30,DAT_004bde30,cVar1);
    }
  }
  return 0;
}

