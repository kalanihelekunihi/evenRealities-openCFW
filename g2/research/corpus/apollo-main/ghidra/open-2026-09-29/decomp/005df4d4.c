
int FUN_005df4d4(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = (**(code **)(param_1 + 0x204))(param_1,param_3,param_2,0);
  if (iVar1 == 0) {
    iVar1 = FT_Stream_ReadFields(param_2,DAT_005e0068,param_1 + 0xa0);
  }
  return iVar1;
}

