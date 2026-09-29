
undefined8 FUN_0055f07a(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10._2_2_ = (undefined2)((uint)param_3 >> 0x10);
  local_10 = CONCAT31(CONCAT21(local_10._2_2_,(char)param_2),(byte)((uint)(param_2 << 0x1c) >> 0x1e)
                     ) & 0xffff03ff;
  uStack_c = param_4;
  if (((local_10._1_1_ == '\0') ||
      (iVar1 = FUN_0055fc2c(*(undefined4 *)(*param_1 + 4),0x304,(int)&local_10 + 1,1),
      iVar1 == DAT_0055f2a8)) &&
     (((char)local_10 == '\0' ||
      (iVar1 = FUN_0055fc2c(*(undefined4 *)(*param_1 + 4),0x307,&local_10,1), iVar1 == DAT_0055f2a8)
      ))) {
    iVar1 = DAT_0055f2a8;
  }
  return CONCAT44(local_10,iVar1);
}

