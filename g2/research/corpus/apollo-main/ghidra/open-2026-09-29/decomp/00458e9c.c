
undefined8
logger_file_size(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar1 = file_open(param_1,0x45904c);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    file_seek(iVar1,0,2);
    iVar2 = file_tell(iVar1);
    file_close(iVar1);
    if (iVar2 < 0) {
      iVar2 = 0;
    }
  }
  return CONCAT44(param_4,iVar2);
}

