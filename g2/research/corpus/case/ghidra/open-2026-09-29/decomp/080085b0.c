
void case_apply_context_options(int *param_1)

{
  if ((*(ushort *)(param_1 + 10) & 1) != 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffdffff | param_1[0xb];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1e) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffeffff | param_1[0xc];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1d) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfffbffff | param_1[0xd];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1c) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffff7fff | param_1[0xe];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1b) < 0) {
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffefff | param_1[0xf];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x1a) < 0) {
    *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffdfff | param_1[0x10];
  }
  if (((int)((uint)*(ushort *)(param_1 + 10) << 0x19) < 0) &&
     (*(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffefffff | param_1[0x11],
     param_1[0x11] == 0x100000)) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xff9fffff | param_1[0x12];
  }
  if ((int)((uint)*(ushort *)(param_1 + 10) << 0x18) < 0) {
    *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xfff7ffff | param_1[0x13];
  }
  return;
}

