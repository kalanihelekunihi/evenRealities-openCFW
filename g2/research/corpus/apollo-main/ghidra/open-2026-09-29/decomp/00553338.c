
undefined8 ensure_text_capacity(int param_1,int *param_2,uint *param_3,uint param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  uint *puVar4;
  
  puVar4 = param_3;
  if (param_1 == 0) {
    uVar1 = 0;
  }
  else if (*param_3 < param_4) {
    uVar3 = *param_3 << 1;
    if (*param_3 << 1 < param_4) {
      uVar3 = param_4;
    }
    iVar2 = file_heap_reallocate(*param_2,uVar3);
    if (iVar2 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        puVar4 = (uint *)0x2a6;
        FUN_0043d574(1,DAT_005533b8,DAT_005533b4,DAT_005533c4,0x2a6,DAT_005533c0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005533c8,DAT_005533c8);
      }
      uVar1 = 0;
    }
    else {
      *param_2 = iVar2;
      *param_3 = uVar3;
      uVar1 = 1;
    }
  }
  else {
    uVar1 = 1;
  }
  return CONCAT44(puVar4,uVar1);
}

