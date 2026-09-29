
undefined8 FUN_00417b62(undefined1 param_1,undefined4 param_2,int param_3)

{
  byte bVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  if ((param_3 == 0) || (iVar2 = get_fmt_enabled(param_1), iVar2 == 0)) {
    bVar1 = 0;
  }
  else {
    bVar1 = 1;
  }
  return CONCAT44(unaff_r7,(uint)bVar1);
}

