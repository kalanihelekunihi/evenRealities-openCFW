/* SPDX-License-Identifier: MIT */
#define MESSAGE(name, text) const char name[] __attribute__((section(".rodata." #name))) = text
MESSAGE(imcra_error_header, "[ImcraStateInit Error] At least sizeof(ImcraState) is required (%d < %d)\n");
MESSAGE(imcra_error_required, "[ImcraStateInit Error] bufsize[%d] < required size[%d]\n");
MESSAGE(imcra_error_space, "[ImcraStateInit Error] Not enough buffer space\n");
MESSAGE(imcra_memory_temp, "Imcra(Temp  )       Memory:%6.2fKB\n");
MESSAGE(imcra_memory_static, "Imcra(Static)       Memory:%6.2fKB\n");
MESSAGE(imcra_memory_total, "Imcra(Total )       Memory:%6.2fKB\n");
