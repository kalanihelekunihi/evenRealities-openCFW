
void gx8002_request_irq(uint param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  
  if ((param_1 < 0x20) && (param_2 != 0)) {
    iVar1 = param_1 * 8 + DAT_1002555c;
    *(int *)(DAT_1002555c + param_1 * 8) = param_2;
    *(undefined4 *)(iVar1 + 4) = param_3;
    csi_vic_enable_irq();
  }
  return;
}

