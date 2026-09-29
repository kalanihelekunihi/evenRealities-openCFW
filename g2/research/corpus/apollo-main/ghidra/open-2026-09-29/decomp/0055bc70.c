
undefined4 dmConnUpdActUpdateMaster(int param_1,int param_2)

{
  undefined4 unaff_r7;
  
  HciLeConnUpdateCmd(*(undefined2 *)(param_1 + 0xc),param_2 + 4);
  return unaff_r7;
}

