#!/usr/bin/env python3
"""Trial-link pinned LVGL providers reachable from Apollo label rendering."""
from pathlib import Path
import hashlib,json,subprocess

repo=Path(__file__).resolve().parents[6]
root=repo/'g2'
submodule=repo/'third-party/upstream/lvgl'
prior=root/'build/c-firmware/root-main-lvgl-label-source-round813'
out=root/'build/c-firmware/root-main-lvgl-label-providers-round814'
out.mkdir(parents=True,exist_ok=True)
def run(args):return subprocess.check_output(args,text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def symbols(path,mode):
    return {line.split()[-1] for line in run(['arm-none-eabi-nm',mode,str(path)]).splitlines()}
commit=run(['git','-C',str(submodule),'rev-parse','HEAD'])
assert commit=='344c7c318047b7348e1be8572a9fd4260c251cfa',commit
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
       '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
       '-DLV_CONF_SKIP','-ffunction-sections','-fdata-sections',
       '-I'+str(root/'components/bootloader/filesystem/freestanding_include'),
       '-I'+str(root/'analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include'),
       '-I'+str(submodule)]
providers={
  'misc/lv_area.c':['lv_area_is_out','lv_point_set'],
  'misc/lv_color.c':['lv_color_black','lv_color_make'],
  'misc/lv_math.c':['lv_trigo_sin'],
  'font/lv_font.c':['lv_font_get_glyph_dsc','lv_font_get_glyph_width',
                    'lv_font_get_line_height','lv_font_glyph_release_draw_data'],
  'draw/lv_draw_rect.c':['lv_draw_fill_dsc_init'],
  'draw/lv_draw_buf.c':['lv_draw_buf_create_ex','lv_draw_buf_destroy'],
  'stdlib/builtin/lv_string_builtin.c':['lv_memcpy','lv_memset'],
  'misc/lv_text.c':['lv_text_encoded_get_char_id',
                    'lv_text_encoded_letter_next_2','lv_text_get_next_line',
                    'lv_text_get_size','lv_text_get_width_with_flags',
                    'lv_text_unicode_to_encoded'],
}
objects=[];source_hashes={};object_hashes={};all_defined=set()
prior_obj=prior/'candidate.o'
prior_defined=symbols(prior_obj,'-g')-symbols(prior_obj,'-u')
for index,(relative,roots) in enumerate(providers.items()):
    source=submodule/'src'/relative
    raw=out/f'lvgl_{index}_raw.o'
    obj=out/f'lvgl_{index}_selected.o'
    subprocess.run(flags+['-c',str(source),'-o',str(raw)],check=True)
    subprocess.run(['arm-none-eabi-ld','-r','--gc-sections']+
                   [item for symbol in roots for item in ('-u',symbol)]+[
                       str(raw),'-o',str(obj)],check=True)
    subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True)
    defined=symbols(obj,'-g')-symbols(obj,'-u')
    assert set(roots)<=defined,(relative,sorted(set(roots)-defined))
    overlap=defined&(prior_defined|all_defined)
    assert not overlap,(relative,sorted(overlap))
    all_defined|=defined
    objects.append(obj)
    source_hashes[relative]=sha(source)
    object_hashes[relative]=sha(obj)
memory_alias=root/'components/main/ambiq_buffer_handlers_candidate_20261014/lvgl_memory_aliases.c'
memory_obj=out/'lvgl_memory_aliases.o'
subprocess.run(flags+['-c',str(memory_alias),'-o',str(memory_obj)],check=True)
memory_defined=symbols(memory_obj,'-g')-symbols(memory_obj,'-u')
assert memory_defined=={'lv_malloc_zeroed','lv_free'},memory_defined
assert not memory_defined&(prior_defined|all_defined)
all_defined|=memory_defined
objects.append(memory_obj)
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(prior_obj)]+[str(p) for p in objects]+
               ['-o',str(candidate)],check=True)
undefined=sorted(symbols(candidate,'-u'))
before=json.loads((prior/'link-audit.json').read_text())
assert 'audio_uart_lv_draw_label_48a0be' not in undefined
assert 'audio_uart_ambiq_vector_shape_draw_5202ec' in undefined
for roots in providers.values():
    for symbol in roots:assert symbol not in undefined,symbol
audit={'status':'trial Apollo LVGL provider C source link',
       'upstream_submodule':'third-party/upstream/lvgl','upstream_commit':commit,
       'provider_sources_sha256':source_hashes,'provider_objects_sha256':object_hashes,
       'memory_alias_source_sha256':sha(memory_alias),
       'memory_alias_object_sha256':sha(memory_obj),
       'candidate_object_sha256':sha(candidate),
       'prior_candidate_object_sha256':sha(prior_obj),
       'defined_provider_symbols':sorted(all_defined),
       'unresolved_before':before['unresolved_after'],
       'unresolved_after':len(undefined),'unresolved_symbols':undefined,
       'compile_profile':'Cortex-M55 Thumb; -fshort-enums; LV_CONF_SKIP defaults; reachable sections only',
       'source_complete':False,'whole_image_linked':False,
       'limits':['Mixed enum-size ELF objects still emit a linker ABI warning.',
                 'Runtime LVGL global state and transitive providers remain.',
                 'No whole-renderer native equivalence, byte equality, or hardware proof.']}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_LVGL_PROVIDER_SOURCE_TRIAL',len(undefined))
