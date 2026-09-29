
void FUN_0045a80a(uint param_1,undefined4 *param_2,int param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  if (param_2 == (undefined4 *)0x0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b13c,0xc2,DAT_0045b118);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0045b120,DAT_0045b120);
    }
  }
  else {
    uVar1 = *param_2;
    FUN_00454b4c(uVar1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0045b100,DAT_0045b0fc,DAT_0045b13c,200,DAT_0045b140,uVar1,param_1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0045b580,DAT_0045b580,uVar1,param_1);
    }
    if (param_3 == 4) {
      FUN_00464b2e(param_1 & 0xffff,0,0,0);
    }
    else {
      FUN_00464b2e(param_1 & 0xffff,param_2 + 1,param_3 - 4U & 0xffff,0);
    }
    file_heap_free(param_2);
  }
  return;
}

