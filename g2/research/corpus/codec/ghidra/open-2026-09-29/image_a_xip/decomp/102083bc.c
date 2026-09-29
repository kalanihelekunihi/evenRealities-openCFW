
undefined4 UartMessageAsyncSend(int *param_1)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = (int *)gx8002_channel_lookup((char)param_1[5]);
  if (((piVar1 != (int *)0x0) && (piVar1[3] != 0)) && ((param_1[6] == 0 || (param_1[4] != 0)))) {
    iVar2 = LvpQueueIsFull(piVar1 + 0x57);
    if (iVar2 == 0) {
      *(ushort *)(param_1 + 2) =
           (ushort)(*(char *)((int)param_1 + 7) != '\0') * 4 + (short)param_1[6];
      if (*param_1 == 0) {
        *param_1 = *piVar1;
      }
      if ((*(ushort *)(param_1 + 1) & 0xff00) != 0x200) {
        iVar2 = piVar1[5];
        *(char *)(piVar1 + 5) = (char)iVar2 + '\x01';
        *(char *)((int)param_1 + 6) = (char)iVar2;
      }
      uVar3 = crc32(0,param_1,10);
      *(short *)((int)param_1 + 10) = (short)uVar3;
      *(short *)(param_1 + 3) = (short)((uint)uVar3 >> 0x10);
      func_0x10025664(param_1,0x10);
      iVar2 = func_0x100261b8(piVar1 + 0x57,param_1);
      if (iVar2 != 0) {
        if (piVar1[6] != 0) {
          return 0;
        }
        gx8002_uart_message_start((char)piVar1[2]);
        return 0;
      }
    }
  }
  return 0xffffffff;
}

