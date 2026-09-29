
undefined8 attcDiscConfigNext(undefined1 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  puVar2 = (undefined4 *)(*(int *)(param_2 + 8) + (uint)*(byte *)(param_2 + 0x12) * 8);
  do {
    if (*(byte *)(param_2 + 0xd) <= *(byte *)(param_2 + 0x12)) {
      uVar1 = 0;
LAB_0056bf10:
      return CONCAT44(param_4,uVar1);
    }
    if (*(short *)(*(int *)(param_2 + 4) + (uint)*(byte *)((int)puVar2 + 5) * 2) != 0) {
      if (*(char *)(puVar2 + 1) == '\0') {
        AttcReadReq(param_1,*(undefined2 *)
                             (*(int *)(param_2 + 4) + (uint)*(byte *)((int)puVar2 + 5) * 2));
      }
      else {
        AttcWriteReq(param_1,*(undefined2 *)
                              (*(int *)(param_2 + 4) + (uint)*(byte *)((int)puVar2 + 5) * 2),
                     *(undefined1 *)(puVar2 + 1),*puVar2);
      }
      uVar1 = 0x79;
      goto LAB_0056bf10;
    }
    *(char *)(param_2 + 0x12) = *(char *)(param_2 + 0x12) + '\x01';
    puVar2 = puVar2 + 2;
  } while( true );
}

