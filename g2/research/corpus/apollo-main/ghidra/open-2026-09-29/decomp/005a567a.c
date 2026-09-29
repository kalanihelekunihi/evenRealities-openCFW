
undefined4 atLsHandler(void)

{
  char cVar1;
  
  cVar1 = atFsListRecursive();
  osDelay(0x1e);
  if (cVar1 == '\0') {
    at_core_output(DAT_005a5710);
  }
  else {
    at_core_output(DAT_005a570c);
  }
  return 1;
}

