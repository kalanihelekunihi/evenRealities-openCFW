
void FUN_0048413c(int *param_1,int param_2,int param_3)

{
  int iVar1;
  
  iVar1 = FUN_004d06ec(param_2,param_3);
  param_1[1] = iVar1;
  if (param_1[1] == 0) {
    FUN_004733ee(DAT_00484360);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  iVar1 = FUN_004416d6(1);
  *param_1 = iVar1;
  if (*param_1 == 0) {
    FUN_004733ee(DAT_00484364);
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  param_1[2] = 0;
  param_1[3] = 0;
  param_1[4] = param_3;
  param_1[5] = param_2;
  return;
}

