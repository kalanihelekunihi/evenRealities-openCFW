
uint gx8002_backup_status(void)

{
  uint uVar1;
  
  if ((uRam00000034 & 1) == 0) {
    if ((uRam00000034 & 4) != 0) {
      return 3;
    }
    if ((uRam00000034 & 8) == 0) {
      if ((uRam00000034 & 2) == 0) {
        uVar1 = uRam0000002c & 1;
      }
      else {
        uVar1 = 4;
      }
    }
    else {
      uVar1 = 5;
    }
  }
  else {
    uVar1 = 2;
  }
  return uVar1;
}

