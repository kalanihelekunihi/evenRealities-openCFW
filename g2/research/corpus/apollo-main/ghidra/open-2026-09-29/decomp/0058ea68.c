
undefined8 FUN_0058ea68(int *param_1,int param_2,byte *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  
  local_10 = param_4;
  if (param_2 == 0) {
    iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),*DAT_0058eaac,&local_10,1);
    iVar1 = DAT_0058eaa8;
    if (iVar2 == DAT_0058eaa8) {
      *param_3 = (byte)local_10 >> 1;
      iVar2 = iVar1;
    }
  }
  else {
    iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),DAT_0058eaac[param_2],param_3,1);
  }
  return CONCAT44(local_10,iVar2);
}

