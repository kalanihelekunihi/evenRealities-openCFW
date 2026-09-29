
void FUN_00551e5c(void)

{
  char cVar1;
  
  cVar1 = service_ancc_message_count_get();
  if (cVar1 == '\0') {
    FUN_0055141c();
    FUN_00551464();
    FUN_005514bc();
  }
  else {
    FUN_00551432();
    FUN_00551448();
    FUN_00551494();
    FUN_00550d3c(cVar1);
    FUN_00550e2e(*DAT_00551ea0,0);
  }
  return;
}

