
void ble_msgtx_set_config(undefined1 param_1,undefined4 param_2,undefined4 param_3)

{
  *DAT_0047826c = param_1;
  *DAT_00478718 = param_2;
  *DAT_00478700 = param_3;
  *DAT_00478720 = DAT_0047871c;
  return;
}

