
void smprScActStoreLescPin(int param_1,int param_2)

{
  undefined *puVar1;
  
  puVar1 = PTR_DAT_005e4210;
  if (*(char *)(*(int *)(param_1 + 0x48) + 1) == '\x03') {
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20,PTR_DAT_005e4210);
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30,puVar1);
    if (*(byte *)(param_2 + 0x14) < 4) {
      WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x2d,param_2 + 4,
                     *(undefined1 *)(param_2 + 0x14));
      WStrReverseCpy(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x3d,param_2 + 4,
                     *(undefined1 *)(param_2 + 0x14));
    }
  }
  return;
}

