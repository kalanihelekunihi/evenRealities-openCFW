
void FUN_004c2b30(void)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = DAT_004c306c;
  if (*DAT_004c306c == '\x01') {
    iVar2 = FUN_00539254();
    if (iVar2 != 0) {
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    iVar2 = FUN_00539304();
    if (iVar2 != 0) {
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
    FUN_00472c7c(0);
    FUN_00480f0c(0x1c,*DAT_004c3200);
    *pcVar1 = '\0';
  }
  return;
}

