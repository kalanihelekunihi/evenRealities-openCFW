
int raccess_guess_linux_double_from_file_name
              (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34 [3];
  undefined4 local_28;
  undefined4 uStack_14;
  
  local_38 = 0;
  local_34[0] = 4;
  local_28 = param_2;
  uStack_14 = param_4;
  iVar1 = FT_Stream_New(param_1,local_34,&local_3c);
  if (iVar1 == 0) {
    iVar1 = raccess_guess_apple_double(param_1,local_3c,param_2,&local_38,param_3);
    FT_Stream_Free(local_3c,0);
  }
  return iVar1;
}

