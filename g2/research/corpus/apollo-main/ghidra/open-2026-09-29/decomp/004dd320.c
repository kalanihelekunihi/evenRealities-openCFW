
void FUN_004dd320(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 local_14 [4];
  undefined4 uStack_10;
  
  iVar2 = *(int *)(param_1 + 0x1c);
  uStack_10 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004dd474,DAT_004dd470,DAT_004dd4f8,0x185,DAT_004dd4f4);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0x10000000,DAT_004dd4fc,DAT_004dd4fc);
  }
  *(undefined1 *)(iVar2 + 0x57c) = 0;
  iVar1 = ui_common_api_fn_00509dfa(*(undefined4 *)(iVar2 + 0x570));
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004dd474,DAT_004dd470,DAT_004dd4f8,0x18c,DAT_004dd500);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004dd504);
    }
    iVar1 = ui_common_api_fn_00509e14(*(undefined4 *)(iVar2 + 0x570),local_14,1);
    if (0 < iVar1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004dd474,DAT_004dd470,DAT_004dd4f8,400,DAT_004dd508,local_14[0]);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_004de140,DAT_004de140,local_14[0]);
      }
      FUN_004de354(iVar2,local_14[0]);
    }
  }
  return;
}

