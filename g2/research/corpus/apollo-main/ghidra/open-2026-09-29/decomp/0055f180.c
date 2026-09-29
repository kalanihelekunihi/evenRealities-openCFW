
undefined8 FUN_0055f180(int *param_1,short *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  
  local_10 = param_4;
  iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),0x308,&local_10,2);
  iVar1 = DAT_0055f2a8;
  if (iVar2 == DAT_0055f2a8) {
    *param_2 = ((ushort)(byte)local_10 * 2 + (ushort)local_10._1_1_) * 2;
    *(short *)(param_1 + 1) = *param_2;
    iVar2 = iVar1;
  }
  return CONCAT44(local_10,iVar2);
}

