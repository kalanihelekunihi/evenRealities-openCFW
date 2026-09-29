
undefined4 compress_log_manager_load(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = file_open(DAT_0044a9c0,&DAT_0044a790);
  piVar1 = DAT_0044a9bc;
  if (iVar2 == 0) {
    *DAT_0044a9bc = DAT_0044a9c4;
    *(undefined1 *)(piVar1 + 1) = 0;
    *(undefined1 *)((int)piVar1 + 5) = 0;
    *(undefined1 *)((int)piVar1 + 6) = 0;
    piVar1[2] = 0;
    *DAT_0044a9c8 = 1;
  }
  else {
    iVar3 = file_read(DAT_0044a9bc,0xc,1,iVar2);
    file_close(iVar2);
    if ((iVar3 != 1) || (*piVar1 != DAT_0044a9c4)) {
      *piVar1 = DAT_0044a9c4;
      *(undefined1 *)(piVar1 + 1) = 0;
      *(undefined1 *)((int)piVar1 + 5) = 0;
      *(undefined1 *)((int)piVar1 + 6) = 0;
      piVar1[2] = 0;
    }
    if (4 < *(byte *)(piVar1 + 1)) {
      *(undefined1 *)(piVar1 + 1) = 0;
    }
    if (4 < *(byte *)((int)piVar1 + 5)) {
      *(undefined1 *)((int)piVar1 + 5) = 0;
    }
    if (5 < *(byte *)((int)piVar1 + 6)) {
      *(undefined1 *)((int)piVar1 + 6) = 0;
    }
    if (DAT_0044a9cc <= (uint)piVar1[2]) {
      piVar1[2] = 0;
    }
    *DAT_0044a9c8 = 1;
    compress_log_manager_reconcile();
  }
  return 0;
}

