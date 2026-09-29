
char vRaisePrivilege(void)

{
  char cVar1;
  bool bVar2;
  char cVar3;
  
  isThreadModePrivileged();
  cVar1 = isUsingMainStack();
  bVar2 = (bool)isCurrentModePrivileged();
  if (bVar2) {
    setThreadModePrivileged(1);
    bVar2 = (bool)isThreadMode();
    if (bVar2) {
      cVar3 = isUsingMainStack();
      setStackMode(cVar3 == '\x01');
    }
  }
  return (cVar1 != '\x01') << 1;
}

