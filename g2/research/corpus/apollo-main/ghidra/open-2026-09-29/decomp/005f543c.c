
undefined4 Ins_JROF(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  if (*(int *)(param_2 + 4) == 0) {
    Ins_JMPR();
  }
  return unaff_r7;
}

