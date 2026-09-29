
void FUN_1000432c(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = DAT_1000433c;
  *(undefined4 *)(DAT_1000433c + param_1 * 4) = param_2;
  *(undefined4 *)(iVar1 + param_1 * 4 + 8) = param_3;
  return;
}

