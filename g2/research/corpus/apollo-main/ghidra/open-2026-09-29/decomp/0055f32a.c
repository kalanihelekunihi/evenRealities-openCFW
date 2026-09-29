
undefined8 FUN_0055f32a(int *param_1,uint *param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar2 = FUN_0055fc38(*(undefined4 *)(*param_1 + 4),0x50a,&local_10,1);
  iVar1 = DAT_0055f730;
  if (iVar2 == DAT_0055f730) {
    *param_2 = local_10 & 0xff;
    iVar2 = iVar1;
  }
  return CONCAT44(local_10,iVar2);
}

