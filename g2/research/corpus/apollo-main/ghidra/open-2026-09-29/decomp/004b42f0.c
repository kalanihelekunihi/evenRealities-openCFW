
undefined4
FUN_004b42f0(byte param_1,int param_2,int param_3,undefined4 param_4,undefined4 param_5,char param_6
            )

{
  char cVar1;
  byte bVar2;
  int iVar3;
  
  iVar3 = ble_ota_mode_get();
  if (iVar3 == 0) {
    cVar1 = FUN_004b32e2(param_1,param_2);
    bVar2 = FUN_004bacf0(1);
    if ((cVar1 == '\0') || (bVar2 < *(byte *)*DAT_004b4718)) {
      for (bVar2 = 0; bVar2 < param_1; bVar2 = bVar2 + 1) {
        if (param_6 != '\0') {
          DmAdvSetInterval(*(undefined1 *)(param_2 + (uint)bVar2),
                           *(undefined2 *)(param_3 + (uint)bVar2 * 2),
                           *(undefined2 *)(param_3 + (uint)bVar2 * 2));
          DmAdvConfig(*(undefined1 *)(param_2 + (uint)bVar2),
                      *(undefined1 *)((uint)*(byte *)(param_2 + (uint)bVar2) + DAT_004b46f4 + 0x59),
                      *(undefined1 *)((uint)*(byte *)(param_2 + (uint)bVar2) + DAT_004b46f4 + 0x6a),
                      DAT_004b46f4 + (uint)*(byte *)(param_2 + (uint)bVar2) * 6 + 0x5e);
        }
        if (*(char *)((uint)*(byte *)(param_2 + (uint)bVar2) + DAT_004b46f4 + 0x55) == '\0') {
          FUN_004b3514(*(undefined1 *)(param_2 + (uint)bVar2),*(undefined1 *)(DAT_004b46f4 + 0x5d));
        }
      }
      DmAdvStart(param_1,param_2,param_4,param_5);
    }
    else {
      for (bVar2 = 0; bVar2 < param_1; bVar2 = bVar2 + 1) {
        *(undefined1 *)(DAT_004b46f4 + (uint)*(byte *)(param_2 + (uint)bVar2) + 0x57) = 3;
      }
    }
  }
  return param_4;
}

