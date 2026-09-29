
undefined4 FUN_005e4902(void)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 unaff_r7;
  
  uVar1 = td_counter_b_get();
  iVar2 = td_record_elapsed_get(uVar1,&stack0xfffffff8);
  if (iVar2 == 0) {
    FUN_005e4894();
  }
  else {
    FUN_005e48b8(unaff_r7);
  }
  return unaff_r7;
}

