
undefined4 smprScActStoreDhCheck(int param_1,int param_2)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = *(int *)(param_2 + 4);
  *(undefined1 *)(param_1 + 0x3f) = 0xf;
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,iVar1 + 9,0x10);
  return unaff_r7;
}

