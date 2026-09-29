
undefined8 compress_log_manager_save(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 in_r3;
  
  iVar2 = file_open(DAT_0044a9c0,&LAB_0044a794);
  puVar1 = DAT_0044a9bc;
  if (iVar2 == 0) {
    uVar3 = 0xffffffff;
  }
  else {
    *DAT_0044a9bc = DAT_0044a9c4;
    iVar4 = file_write(puVar1,0xc,1,iVar2);
    file_close(iVar2);
    if (iVar4 == 1) {
      uVar3 = 0;
    }
    else {
      uVar3 = 0xffffffff;
    }
  }
  return CONCAT44(in_r3,uVar3);
}

