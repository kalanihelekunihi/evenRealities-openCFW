
undefined8 td_current_record(int param_1)

{
  int iVar1;
  int unaff_r7;
  
  if (param_1 == -1) {
    if (*(int *)(DAT_00597c08 + 0x956c) == -1) {
      iVar1 = DAT_00597c08 + 0x956c;
    }
    else {
      iVar1 = 0;
    }
  }
  else {
    iVar1 = td_find_record_index(param_1,&stack0xfffffff8);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar1 = DAT_00597c08 + unaff_r7 * 0x90 + 0x95fc;
    }
  }
  return CONCAT44(unaff_r7,iVar1);
}

