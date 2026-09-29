
undefined4 semantic_whitelist_file_size_preserving_position(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  
  if (param_1 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    iVar2 = file_tell(param_1);
    if (iVar2 < 0) {
      uVar1 = 0xffffffff;
    }
    else {
      iVar3 = file_seek(param_1,0,2);
      if (iVar3 == 0) {
        uVar1 = file_tell(param_1);
        file_seek(param_1,iVar2,0);
      }
      else {
        uVar1 = 0xffffffff;
      }
    }
  }
  return uVar1;
}

