
int FUN_005d352e(int param_1,int param_2,int param_3,int param_4)

{
  return (int)(short)((uint)param_1 >> 0x10) * (int)(short)((uint)(param_4 - param_2) >> 0x10) -
         (int)(short)((uint)param_2 >> 0x10) * (int)(short)((uint)(param_3 - param_1) >> 0x10);
}

