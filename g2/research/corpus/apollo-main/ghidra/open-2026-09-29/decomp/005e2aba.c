
void smpScAuthReq(int param_1,undefined1 param_2,undefined1 param_3)

{
  ushort uStack_20;
  undefined1 uStack_1e;
  undefined1 uStack_1c;
  undefined1 uStack_1b;
  undefined1 uStack_1a;
  undefined1 uStack_c;
  
  if (((**(char **)(param_1 + 0x48) == '\0') && ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0)
      ) || ((**(char **)(param_1 + 0x48) != '\0' &&
            (*(char *)(*(int *)(param_1 + 0x48) + 1) == '\x02')))) {
    uStack_20 = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_1e = 0x2e;
    uStack_1c = param_2;
    uStack_1b = param_3;
    DmSmpCbackExec(&uStack_20);
  }
  else {
    uStack_20 = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_1e = 4;
    uStack_1c = 0;
    uStack_1b = 0;
    uStack_1a = 0;
    uStack_c = 3;
    smpSmExecute(param_1,&uStack_20);
  }
  return;
}

