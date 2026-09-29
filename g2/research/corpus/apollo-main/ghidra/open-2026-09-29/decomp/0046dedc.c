
undefined8 _bleSlaveRequestMtuExchange(undefined2 *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined2 uVar1;
  int *piVar2;
  undefined2 uVar3;
  int iVar4;
  
  uVar1 = *param_1;
  uVar3 = AttGetMtu((char)uVar1);
  piVar2 = DAT_0046e010;
  *(undefined2 *)(*DAT_0046e010 + 0x22) = uVar3;
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    param_2 = 0x130;
    param_3 = DAT_0046e074;
    FUN_0043d574(4,DAT_0046dff8,DAT_0046dff4,DAT_0046e078,0x130,DAT_0046e074,
                 *(undefined2 *)(*piVar2 + 0x22));
  }
  iVar4 = FUN_0043d0ce();
  if (-1 < iVar4 << 0x1f) {
    iVar4 = FUN_0043d0ce();
    if (-1 < iVar4 << 0x1d) goto LAB_0046df32;
  }
  compress_log_output(0x10400000,DAT_0046e07c,DAT_0046e07c,*(undefined2 *)(*piVar2 + 0x22));
LAB_0046df32:
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    param_2 = 0x131;
    param_3 = DAT_0046e080;
    FUN_0043d574(4,DAT_0046dff8,DAT_0046dff4,DAT_0046e078,0x131,DAT_0046e080,0xf7);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046e084,DAT_0046e084,0xf7);
  }
  AttcMtuReq((char)uVar1,0xf7);
  return CONCAT44(param_3,param_2);
}

