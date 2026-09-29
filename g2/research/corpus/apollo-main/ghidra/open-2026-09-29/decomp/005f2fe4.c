
undefined8 TT_Set_MM_Blend(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = tt_set_mm_blend(param_1,param_2,param_3,1);
  if (iVar1 == 0) {
    if (param_2 == 0) {
      *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) & 0xffff7fff;
    }
    else {
      *(uint *)(param_1 + 8) = *(uint *)(param_1 + 8) | 0x8000;
    }
    iVar1 = 0;
  }
  return CONCAT44(param_4,iVar1);
}

