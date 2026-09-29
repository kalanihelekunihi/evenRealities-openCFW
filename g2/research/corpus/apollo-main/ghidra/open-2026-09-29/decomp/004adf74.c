
undefined4
als_function_25(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  short sVar2;
  int iVar3;
  int iVar4;
  
  FUN_00509024(9,1,param_3,param_4,param_1,param_2,param_3,param_4);
  osDelay(5);
  iVar3 = DAT_004ae958;
  ti_opt3007_assignRegistermap(DAT_004ae958);
  sVar1 = FUN_005135d2(iVar3 + 0x33);
  sVar2 = FUN_005135d2(iVar3 + 0x36);
  if ((sVar1 == 0x5449) && (sVar2 == 0x3001)) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae960,0x193,DAT_004ae968,0x5449,0x3001);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_004ae96c,DAT_004ae96c,0x5449,0x3001);
    }
    FUN_0051357c(iVar3 + 0xc,3);
    FUN_0051357c(iVar3 + 9,0);
    return 0;
  }
  iVar3 = FUN_0043d0ce();
  if (iVar3 << 0x1e < 0) {
    FUN_0043d574(1,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae960,400,DAT_004ae95c);
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x4000000,DAT_004ae964,DAT_004ae964);
  }
  return 0xffffffff;
}

