
uint gx8002_backup_preserve_memory(void)

{
  int iVar1;
  
  iVar1 = gx8002_backup_status();
  if (iVar1 - 2U < 4) {
    return uRam00000058 & 1;
  }
  return 0;
}

