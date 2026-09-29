
void FUN_0800adb8(int param_1)

{
  char cVar1;
  
  cVar1 = *(char *)(param_1 + 0x59);
  if (cVar1 == '\0') {
    FUN_0800c030(*(undefined4 *)(param_1 + 0x30));
    FUN_0800c030(param_1);
  }
  else {
    if (cVar1 == '\x01') {
      FUN_0800c030(param_1);
      return;
    }
    if (cVar1 != '\x02') {
      disableIRQinterrupts();
      do {
                    /* WARNING: Do nothing block with infinite loop */
      } while( true );
    }
  }
  return;
}

