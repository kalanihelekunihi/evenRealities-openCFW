
undefined8 FUN_0055fc74(undefined4 *param_1,uint *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint local_10;
  
  local_10 = param_4;
  iVar2 = FUN_0055fc38(*param_1,0xb04,&local_10,1);
  iVar1 = DAT_0055fcb0;
  if (iVar2 == DAT_0055fcb0) {
    *param_2 = local_10 & 7;
    *(byte *)(param_2 + 1) = (byte)local_10 >> 3 & 1;
    *(char *)(param_1 + 1) = (char)param_2[1];
    iVar2 = iVar1;
  }
  return CONCAT44(local_10,iVar2);
}

