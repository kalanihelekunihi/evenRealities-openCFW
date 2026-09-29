
void APP_MasterSetTargetAddrName(int param_1,int param_2,undefined1 param_3)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  
  puVar1 = DAT_004a26cc;
  if (param_1 != 0) {
    FUN_00439be4(DAT_004a26cc,param_1,6);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,DAT_004a28fc,0x478,DAT_004a28f8,puVar1[5],puVar1[4],
                   puVar1[3],puVar1[2],puVar1[1],*puVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x11800000,DAT_004a2900,DAT_004a2900,puVar1[5],puVar1[4],puVar1[3],
                          puVar1[2],puVar1[1],*puVar1);
    }
  }
  uVar2 = DAT_004a2904;
  if (param_2 != 0) {
    FUN_0043c0e4(DAT_004a2904,0xf,0);
    FUN_00439be4(uVar2,param_2,param_3);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004a28f0,DAT_004a28ec,DAT_004a28fc,0x47e,DAT_004a2908,uVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_004a2c6c,DAT_004a2c6c,uVar2);
    }
  }
  return;
}

