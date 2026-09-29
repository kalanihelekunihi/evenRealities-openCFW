
void FUN_0045abc4(undefined4 param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  undefined2 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  int iVar5;
  
  if (param_2 == (undefined4 *)0x0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b6e0,0x112,DAT_0045b118);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0045b120);
    }
  }
  else {
    uVar1 = *param_2;
    uVar2 = *(undefined2 *)(param_2 + 1);
    uVar3 = *(undefined4 *)((int)param_2 + 6);
    uVar4 = *(undefined4 *)((int)param_2 + 10);
    FUN_00454b4c(uVar1);
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0045b100,DAT_0045b0fc,DAT_0045b6e0,0x11a,DAT_0045b140,uVar1,param_1);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0045b580,DAT_0045b580,uVar1,param_1);
    }
    FUN_00465748(uVar2,uVar3,uVar4,0);
    file_heap_free(param_2);
  }
  return;
}

