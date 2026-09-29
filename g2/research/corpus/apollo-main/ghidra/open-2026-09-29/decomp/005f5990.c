
void Ins_SPVTL(int param_1,uint *param_2)

{
  int iVar1;
  
  iVar1 = Ins_SxVTL(param_1,param_2[1] & 0xffff,*param_2 & 0xffff,param_1 + 0x12a);
  if (iVar1 == 0) {
    *(undefined4 *)(param_1 + 0x126) = *(undefined4 *)(param_1 + 0x12a);
    Compute_Funcs(param_1);
  }
  return;
}

