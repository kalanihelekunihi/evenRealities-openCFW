
void load_sbit_image(int param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  ushort local_24;
  ushort local_22;
  short local_20;
  short local_1e;
  ushort local_1c;
  short local_1a;
  short local_18;
  ushort local_16;
  
  iVar1 = *(int *)(param_2 + 4);
  iVar1 = (**(code **)(*(int *)(iVar1 + 0x21c) + 0x48))
                    (iVar1,*(undefined4 *)(param_1 + 0x74),param_3,param_4,
                     *(undefined4 *)(iVar1 + 0x68),param_2 + 0x4c,&local_24);
  if (iVar1 == 0) {
    *(undefined2 *)(param_2 + 0x6e) = 0;
    *(undefined2 *)(param_2 + 0x6c) = 0;
    *(uint *)(param_2 + 0x18) = (uint)local_22 << 6;
    *(uint *)(param_2 + 0x1c) = (uint)local_24 << 6;
    *(int *)(param_2 + 0x20) = (int)local_20 << 6;
    *(int *)(param_2 + 0x24) = (int)local_1e << 6;
    *(uint *)(param_2 + 0x28) = (uint)local_1c << 6;
    *(int *)(param_2 + 0x2c) = (int)local_1a << 6;
    *(int *)(param_2 + 0x30) = (int)local_18 << 6;
    *(uint *)(param_2 + 0x34) = (uint)local_16 << 6;
    *(undefined4 *)(param_2 + 0x48) = DAT_005f1560;
    if (param_4 << 0x1b < 0) {
      *(int *)(param_2 + 100) = (int)local_1a;
      *(int *)(param_2 + 0x68) = (int)local_18;
    }
    else {
      *(int *)(param_2 + 100) = (int)local_20;
      *(int *)(param_2 + 0x68) = (int)local_1e;
    }
  }
  return;
}

