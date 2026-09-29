
undefined8 FUN_005eb30c(void)

{
  byte bVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  iVar2 = td_session_struct_ptr();
  if (iVar2 == 0) {
    bVar1 = 0;
  }
  else {
    bVar1 = (byte)*(undefined2 *)(iVar2 + 0x406);
  }
  return CONCAT44(unaff_r7,(uint)bVar1);
}

