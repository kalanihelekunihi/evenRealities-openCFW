
char FUN_004c8d3c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 *param_5)

{
  char cVar1;
  
  if (param_5 != (undefined4 *)0x0) {
    *param_5 = 0;
  }
  cVar1 = FUN_004c6fba(param_1,param_2,0);
  if ((cVar1 == '\0') && (cVar1 = FUN_004c6f46(param_1,param_3,param_4,param_5), cVar1 == '\0')) {
    cVar1 = '\0';
  }
  return cVar1;
}

