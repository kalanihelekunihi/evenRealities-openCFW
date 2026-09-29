
void compress_log_rotate_file(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  uint uVar5;
  undefined1 auStack_40 [48];
  undefined4 uStack_10;
  
  iVar1 = DAT_0044a9bc;
  uVar5 = (*(byte *)(DAT_0044a9bc + 4) + 1) % 5;
  uStack_10 = in_r3;
  if (*(byte *)(DAT_0044a9bc + 6) < 5) {
    *(char *)(DAT_0044a9bc + 6) = *(char *)(DAT_0044a9bc + 6) + '\x01';
  }
  else {
    compress_log_file_remove(*(undefined1 *)(DAT_0044a9bc + 5));
    uVar2 = *(byte *)(iVar1 + 5) + 1;
    *(char *)(iVar1 + 5) = (char)uVar2 + (char)(uVar2 / 5) * -5;
  }
  *(char *)(iVar1 + 4) = (char)uVar5;
  *(undefined4 *)(iVar1 + 8) = 0;
  compress_log_path_format(uVar5,auStack_40,0x30);
  iVar3 = file_open(auStack_40,&LAB_0044a794);
  if (iVar3 != 0) {
    iVar4 = _write_file_version_header(iVar3);
    if (iVar4 != 0) {
      *(int *)(iVar1 + 8) = iVar4;
    }
    file_close(iVar3);
  }
  compress_log_manager_save();
  return;
}

