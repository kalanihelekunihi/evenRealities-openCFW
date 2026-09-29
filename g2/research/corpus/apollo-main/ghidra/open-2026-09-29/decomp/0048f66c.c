
undefined8 FUN_0048f66c(undefined4 param_1,byte *param_2,uint *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined1 *local_10;
  
  *param_4 = 0;
  *param_2 = 0;
  *param_3 = 0;
  local_10 = param_4;
  iVar1 = FUN_0048f4b8(param_1,&local_10,param_4);
  if (iVar1 != 0) {
    *param_3 = (uint)local_10 >> 3;
    *param_2 = (byte)local_10 & 7;
  }
  return CONCAT44(local_10,(uint)(iVar1 != 0));
}

