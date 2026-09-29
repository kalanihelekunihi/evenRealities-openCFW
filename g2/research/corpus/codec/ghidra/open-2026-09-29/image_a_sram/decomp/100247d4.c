
void gx8002_flash_type_api(int param_1)

{
  if (*(uint *)(param_1 + 0x30) != 0) {
    (*(code *)(*(uint *)(param_1 + 0x30) & 0xfffffffe))();
  }
  return;
}

