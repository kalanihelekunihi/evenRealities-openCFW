
void FUN_005d071c(undefined4 *param_1,char *param_2)

{
  char *pcVar1;
  
  for (pcVar1 = (char *)*param_1; ((pcVar1 < param_2 && (*pcVar1 != '\r')) && (*pcVar1 != '\n'));
      pcVar1 = pcVar1 + 1) {
  }
  *param_1 = pcVar1;
  return;
}

