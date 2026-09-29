
bool FUN_004d46c2(int *param_1)

{
  int iVar1;
  
  iVar1 = *param_1;
  if (iVar1 != 0) {
    vQueueDelete(param_1[1]);
    *param_1 = 0;
  }
  return iVar1 != 0;
}

