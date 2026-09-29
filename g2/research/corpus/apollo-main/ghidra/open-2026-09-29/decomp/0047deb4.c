
undefined8 FUN_0047deb4(int *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  uint local_10;
  
  local_10 = param_4;
  FUN_0043c0e4(param_1,0xc,0);
  param_1[1] = -1;
  iVar1 = file_opendir(DAT_0047e29c);
  if (iVar1 == 0) {
    uVar2 = 0xfffffffb;
  }
  else {
    while (iVar3 = file_readdir(iVar1), iVar3 != 0) {
      if ((*(char *)(iVar3 + 0x100) == '\b') && (iVar3 = FUN_0047de18(iVar3,&local_10), iVar3 != 0))
      {
        *param_1 = *param_1 + 1;
        if (local_10 < (uint)param_1[1]) {
          param_1[1] = local_10;
        }
        if ((uint)param_1[2] < local_10) {
          param_1[2] = local_10;
        }
      }
    }
    file_closedir(iVar1);
    uVar2 = 0;
  }
  return CONCAT44(local_10,uVar2);
}

