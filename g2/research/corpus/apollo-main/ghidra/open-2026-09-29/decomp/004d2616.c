
undefined4 dmPrivActRemDevFromResList(undefined2 *param_1)

{
  undefined4 unaff_r7;
  
  *(undefined2 *)(DAT_004d2920 + 6) = *param_1;
  HciLeRemoveDeviceFromResolvingList(*(undefined1 *)(param_1 + 2),(int)param_1 + 5);
  return unaff_r7;
}

