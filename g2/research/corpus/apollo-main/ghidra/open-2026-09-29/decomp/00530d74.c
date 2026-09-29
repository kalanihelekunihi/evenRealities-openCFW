
bool attcPendWriteCmd(int param_1,short param_2)

{
  bool bVar1;
  char cVar2;
  
  cVar2 = '\0';
  bVar1 = false;
  do {
    if (bVar1) {
      return cVar2 != '\0';
    }
    if (*(short *)(param_1 + 0x2a) != 0) {
      if (*(short *)(param_1 + 0x2a) == param_2) {
        return true;
      }
      cVar2 = cVar2 + '\x01';
    }
    bVar1 = true;
  } while( true );
}

