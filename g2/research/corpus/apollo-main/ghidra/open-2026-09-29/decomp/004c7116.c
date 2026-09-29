
void FUN_004c7116(undefined4 *param_1,char *param_2)

{
  char *pcVar1;
  undefined4 local_8;
  
  local_8 = CONCAT31(local_8._1_3_,*param_2);
  pcVar1 = param_2;
  if ((*param_2 != '\0') && (pcVar1 = param_2 + 1, *pcVar1 == ':')) {
    pcVar1 = param_2 + 2;
  }
  *param_1 = local_8;
  param_1[1] = pcVar1;
  return;
}

