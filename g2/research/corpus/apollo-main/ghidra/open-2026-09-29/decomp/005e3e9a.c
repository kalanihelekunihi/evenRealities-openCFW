
undefined4 smprScActPkStoreCnf(int param_1,int param_2)

{
  undefined4 unaff_r7;
  
  WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x50,*(int *)(param_2 + 4) + 9,0x10);
  return unaff_r7;
}

