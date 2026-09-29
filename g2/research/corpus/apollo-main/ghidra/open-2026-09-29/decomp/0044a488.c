
bool compress_log_file_exists(undefined1 param_1)

{
  int iVar1;
  undefined1 auStack_38 [48];
  
  compress_log_path_format(param_1,auStack_38,0x30);
  iVar1 = file_open(auStack_38,&DAT_0044a790);
  if (iVar1 != 0) {
    file_close();
  }
  return iVar1 != 0;
}

