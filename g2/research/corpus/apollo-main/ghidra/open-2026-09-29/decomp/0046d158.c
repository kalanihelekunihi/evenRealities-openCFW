
undefined8 FUN_0046d158(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if ((param_1 != 0) && (param_2 != 0)) {
    piVar1 = (int *)file_heap_allocate(0xc);
    if (piVar1 == (int *)0x0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_14 = DAT_0046d5f4;
        local_18 = 0x156;
        FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d5f8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0046d5fc,DAT_0046d5fc);
      }
    }
    else {
      *piVar1 = param_2;
      *(char *)(piVar1 + 1) = (char)param_3;
      piVar1[2] = *(int *)(param_1 + 4);
      *(int **)(param_1 + 4) = piVar1;
    }
  }
  return CONCAT44(local_14,local_18);
}

