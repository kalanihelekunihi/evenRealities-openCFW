
undefined8 FUN_0055f218(int *param_1,undefined2 *param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  uint local_10;
  
  local_10 = param_4;
  iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),0x30a,&local_10,2);
  iVar1 = DAT_0055f2a8;
  if (iVar2 == DAT_0055f2a8) {
    *param_2 = (short)((((local_10 & 0xff) * 2 + (local_10 >> 8 & 0xff)) * 0x143) / 100);
    *(undefined2 *)((int)param_1 + 6) = *param_2;
    iVar2 = iVar1;
  }
  return CONCAT44(local_10,iVar2);
}

