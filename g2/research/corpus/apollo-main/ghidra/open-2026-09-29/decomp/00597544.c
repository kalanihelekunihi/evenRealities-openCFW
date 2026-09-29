
undefined8 td_record_in_use_get(undefined4 param_1)

{
  byte bVar1;
  int iVar2;
  int unaff_r7;
  
  iVar2 = td_find_record_index(param_1,&stack0xfffffff8);
  if ((iVar2 == 0) || (*(char *)(DAT_00597c08 + unaff_r7 * 0x90 + 0x9688) == '\0')) {
    bVar1 = 0;
  }
  else {
    bVar1 = 1;
  }
  return CONCAT44(unaff_r7,(uint)bVar1);
}

