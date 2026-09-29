
void gx8002_backup_request_irq(uint param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = DAT_10004864;
  if ((param_1 < 0x20) && (param_2 != 0)) {
    *(int *)(DAT_10004864 + param_1 * 8) = param_2;
    *(undefined4 *)(iVar1 + param_1 * 8 + 4) = param_3;
    *DAT_10004868 = 1 << (param_1 & 0x3f);
  }
  return;
}

