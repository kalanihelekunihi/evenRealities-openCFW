
void smpScActCalcF5TKey(int param_1,int param_2)

{
  int iVar1;
  undefined1 auStack_24 [16];
  
  if (*(char *)(param_2 + 3) == '\0') {
    smpLogByteArray(DAT_005e3108,param_2 + 4,0x20);
    iVar1 = SmpScAlloc(0x20,param_1,param_2);
    if (iVar1 != 0) {
      FUN_00439c04(auStack_24,DAT_005e310c,0x10);
      FUN_00439be4(iVar1,param_2 + 4,0x20);
      SmpScCmac(auStack_24,iVar1,0x20,param_1,param_2);
    }
  }
  else {
    SmpScGetCancelMsgWithReattempt(*(undefined1 *)(param_1 + 0x3d),param_2,0xb);
    smpSmExecute(param_1,param_2);
  }
  return;
}

