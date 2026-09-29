
undefined4 text_stream_copy_bytes(int *param_1,uint param_2,char param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_1 != (int *)0x0) {
    if ((param_1[8] != 0) && (iVar1 = osMutexAcquire(param_1[8],0xffffffff), iVar1 == 0)) {
      if ((param_1[4] & 0xffffU) < (param_2 & 0xffff)) {
        param_2 = param_1[4];
      }
      iVar1 = ensure_text_capacity(param_1,param_1,param_1 + 9,(param_2 & 0xffff) + 1);
      if (iVar1 == 0) {
        osMutexRelease(param_1[8]);
        return param_4;
      }
      FUN_00439be4(*param_1,param_1[1],param_2 & 0xffff);
      *(undefined1 *)(*param_1 + (param_2 & 0xffff)) = 0;
      param_1[3] = param_2 & 0xffff;
      osMutexRelease(param_1[8]);
    }
    if ((param_3 != '\0') && (param_1[6] != 0)) {
      (*(code *)param_1[6])(*param_1);
    }
  }
  return param_4;
}

