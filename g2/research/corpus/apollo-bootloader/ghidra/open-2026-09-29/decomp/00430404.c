
undefined8 FUN_00430404(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  iVar1 = DAT_00430468;
  local_10 = param_3;
  uStack_c = param_4;
  FUN_0041df48((int)*(short *)(DAT_00430468 + 2),0,&local_10);
  FUN_0041dfc6((int)*(short *)(iVar1 + 2),local_10);
  FUN_0041e09a((int)*(short *)(iVar1 + 2),local_10);
  return CONCAT44(uStack_c,local_10);
}

