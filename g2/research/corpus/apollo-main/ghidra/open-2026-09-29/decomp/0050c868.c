
undefined8 FUN_0050c868(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 local_18 [3];
  
  local_18[0] = param_2;
  local_18[1] = param_3;
  local_18[2] = param_4;
  FUN_0050c3c0();
  if (*(int *)(DAT_0050c97c + 0xc0) != 0) {
    local_18[0] = *DAT_0050ca20;
    local_18[1] = DAT_0050ca20[1];
    local_18[2] = DAT_0050ca20[2];
    for (iVar3 = 0; iVar3 < 3; iVar3 = iVar3 + 1) {
      iVar1 = FUN_0050c476(local_18[iVar3]);
      if (((iVar1 != 0) && (*(char *)(iVar1 + 0x29) == '\0')) &&
         (iVar2 = FUN_0050c8cc(), -1 < iVar2)) {
        FUN_0050c314(iVar1);
      }
    }
  }
  return CONCAT44(local_18[1],local_18[0]);
}

