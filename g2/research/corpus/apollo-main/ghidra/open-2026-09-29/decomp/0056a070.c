
void hciEvtParseVendorSpecCmdCmpl(int param_1,undefined1 *param_2,char param_3)

{
  byte bVar1;
  
  bVar1 = param_3 - 1;
  if ((2 < bVar1) && ((int)(bVar1 - 3) < 0x83)) {
    *(ushort *)(param_1 + 4) = (ushort)(byte)param_2[-1] * 0x100 + (ushort)(byte)param_2[-2];
    *(undefined1 *)(param_1 + 3) = *param_2;
    FUN_00439be4(param_1 + 6,param_2 + 1,bVar1 - 3);
  }
  return;
}

