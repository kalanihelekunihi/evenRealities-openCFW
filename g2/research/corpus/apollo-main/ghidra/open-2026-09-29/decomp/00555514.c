
void FUN_00555514(int param_1,undefined4 param_2)

{
  int iVar1;
  
  if (param_1 != 0) {
    iVar1 = teleprompt_page_data_get(param_2);
    if (iVar1 == 0) {
      FUN_0049942e(param_1,&DAT_00555748);
    }
    else {
      FUN_0049942e(param_1,iVar1 + 10);
    }
  }
  return;
}

