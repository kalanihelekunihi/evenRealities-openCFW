
void FUN_004f55e0(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  ushort uVar2;
  
  if ((param_1 != (undefined4 *)0x0) && (param_2 != 0)) {
    *(undefined4 *)(param_2 + 0x10c) = *param_1;
    *(undefined4 *)(param_2 + 0x110) = param_1[1];
    *(char *)(param_2 + 0x121) = (char)param_1[2];
    uVar1 = param_1[5];
    *(undefined4 *)(param_2 + 0x118) = param_1[4];
    *(undefined4 *)(param_2 + 0x11c) = uVar1;
    *(undefined1 *)(param_2 + 0x120) = *(undefined1 *)(param_1 + 6);
    if (*(ushort *)((int)param_1 + 0xe2) < 0xc9) {
      uVar2 = *(ushort *)((int)param_1 + 0xe2);
    }
    else {
      uVar2 = 200;
    }
    FUN_00439be4(param_2,(int)param_1 + 0x19,uVar2);
    *(undefined1 *)(param_2 + (uint)uVar2) = 0;
  }
  return;
}

