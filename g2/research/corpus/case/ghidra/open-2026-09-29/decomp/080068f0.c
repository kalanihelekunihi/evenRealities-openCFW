
void case_initialize_transport_record(void)

{
  int *piVar1;
  int iVar2;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  piVar1 = DAT_08006960;
  iVar2 = DAT_0800695c;
  local_18 = 0;
  local_14 = 0;
  local_10 = 0;
  *DAT_08006960 = DAT_0800695c;
  piVar1[2] = 0;
  piVar1[3] = 0;
  piVar1[4] = 0;
  piVar1[1] = iVar2 << 0x14;
  piVar1[5] = 4;
  *(undefined1 *)(piVar1 + 6) = 0;
  *(undefined1 *)((int)piVar1 + 0x19) = 0;
  *(undefined1 *)((int)piVar1 + 0x1a) = 1;
  piVar1[7] = 1;
  *(undefined1 *)(piVar1 + 8) = 0;
  piVar1[9] = 0;
  piVar1[10] = 0;
  *(undefined1 *)(piVar1 + 0xb) = 0;
  piVar1[0xc] = 0;
  piVar1[0xe] = 0;
  piVar1[0xd] = 5;
  *(undefined1 *)(piVar1 + 0xf) = 0;
  piVar1[0x13] = 0;
  iVar2 = FUN_08004480();
  if (iVar2 != 0) {
    case_fail_stop();
  }
  local_18 = DAT_08006964;
  local_14 = 0;
  local_10 = 0;
  iVar2 = case_configure_pin_policy(DAT_08006960,&local_18);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  case_calibrate_controller(DAT_08006960);
  return;
}

