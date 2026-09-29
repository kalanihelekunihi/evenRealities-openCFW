
void dmPrivActAddDevToResList(undefined2 *param_1)

{
  int iVar1;
  
  iVar1 = DAT_004d2920;
  *(undefined1 *)(DAT_004d2920 + 8) = *(undefined1 *)((int)param_1 + 0x2b);
  *(undefined2 *)(iVar1 + 4) = *param_1;
  HciLeAddDeviceToResolvingListCmd
            (*(undefined1 *)(param_1 + 2),(int)param_1 + 5,(int)param_1 + 0xb,(int)param_1 + 0x1b);
  return;
}

