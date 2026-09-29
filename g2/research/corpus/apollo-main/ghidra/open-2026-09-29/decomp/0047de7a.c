
undefined8 FUN_0047de7a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = file_open(param_1,&DAT_0047e140);
  if (iVar1 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = 0;
    iVar3 = file_seek(iVar1,0,2);
    if (iVar3 == 0) {
      iVar2 = file_tell(iVar1);
    }
    file_close(iVar1);
    if (iVar2 < 1) {
      iVar2 = 0;
    }
  }
  return CONCAT44(param_4,iVar2);
}

