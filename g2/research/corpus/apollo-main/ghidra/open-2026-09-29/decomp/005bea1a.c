
longlong FUN_005bea1a(int param_1,int param_2,undefined4 param_3,uint param_4)

{
  FUN_005bdfca(param_1,param_2,0);
  (**(code **)(param_2 + 0x24))(*(undefined4 *)(param_2 + 0x28),*(undefined4 *)(param_1 + 0x28));
  (**(code **)(param_2 + 0x24))(*(undefined4 *)(param_2 + 0x28),*(undefined4 *)(param_1 + 0x24));
  (**(code **)(param_2 + 0x24))(*(undefined4 *)(param_2 + 0x28),param_1);
  return (ulonglong)param_4 << 0x20;
}

