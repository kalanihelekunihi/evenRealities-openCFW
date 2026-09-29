
undefined4 td_session_struct_copy_out(int param_1)

{
  undefined4 uVar1;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    FUN_00439be4(DAT_00597c0c,param_1,0x84c);
    uVar1 = 0;
  }
  return uVar1;
}

