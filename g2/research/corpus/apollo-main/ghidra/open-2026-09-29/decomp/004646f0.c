
int FUN_004646f0(undefined4 param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = 0;
  iVar4 = 1;
  iVar2 = 0;
  while ((iVar3 < 10 && (iVar2 = file_heap_allocate(param_1), iVar2 == 0))) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004651b8,DAT_004651b4,DAT_004651b0,0x1e,DAT_004651ac,iVar3 + 1,10,iVar4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8c00000,DAT_004651bc,DAT_004651bc,iVar3 + 1,10,iVar4);
    }
    osDelay(iVar4);
    iVar4 = iVar4 << 1;
    iVar3 = iVar3 + 1;
  }
  return iVar2;
}

