
void compress_log_file_remove(undefined1 param_1)

{
  undefined1 auStack_38 [48];
  
  compress_log_path_format(param_1,auStack_38,0x30);
  file_remove(auStack_38);
  return;
}

