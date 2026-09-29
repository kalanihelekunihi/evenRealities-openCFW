
undefined8 FUN_0055f54e(int *param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  
  local_10 = param_4;
  iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),0x509,&local_10,1);
  iVar1 = DAT_0055f730;
  if (iVar2 == DAT_0055f730) {
    *param_2 = (byte)local_10 & 1;
    param_2[1] = (byte)local_10 >> 1 & 1;
    *(byte *)(param_1 + 1) = param_2[1];
    iVar2 = iVar1;
  }
  return CONCAT44(local_10,iVar2);
}

