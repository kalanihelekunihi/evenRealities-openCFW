
undefined8 FUN_0050668e(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int local_10;
  
  local_10 = param_4;
  iVar1 = FUN_00508e5c(param_1,0xa267,1,&local_10);
  if (iVar1 == 0) {
    *(byte *)(param_1 + 0x11) = (byte)((uint)(local_10 << 0x1e) >> 0x1f);
  }
  return CONCAT44(local_10,iVar1);
}

