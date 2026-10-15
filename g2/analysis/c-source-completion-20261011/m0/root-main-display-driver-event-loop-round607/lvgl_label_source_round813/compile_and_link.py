#!/usr/bin/env python3
"""Trial-link the pinned LVGL label source with the Apollo C candidate."""
from pathlib import Path
import hashlib,json,subprocess

repo=Path(__file__).resolve().parents[6]
root=repo/'g2'
submodule=repo/'third-party/upstream/lvgl'
source=submodule/'src/draw/lv_draw_label.c'
probe=Path(__file__).resolve().parent/'layout_probe.c'
prior=root/'build/c-firmware/root-main-uled-option-fifteen-label-pixel-lower-integration-round812'
out=root/'build/c-firmware/root-main-lvgl-label-source-round813'
out.mkdir(parents=True,exist_ok=True)
def run(args):return subprocess.check_output(args,text=True).strip()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
commit=run(['git','-C',str(submodule),'rev-parse','HEAD'])
assert commit=='344c7c318047b7348e1be8572a9fd4260c251cfa',commit
includes=['-I'+str(root/'components/bootloader/filesystem/freestanding_include'),
          '-I'+str(root/'analysis/c-source-completion-20261011/peripherals/root-freetype-class-build-round406/freestanding_include'),
          '-I'+str(submodule)]
flags=['clang','--target=arm-none-eabi','-mcpu=cortex-m55','-mthumb',
       '-fshort-enums','-std=c11','-ffreestanding','-fno-builtin','-O2',
       '-DLV_CONF_SKIP']+includes
subprocess.run(flags+['-c',str(probe),'-o',str(out/'layout_probe.o')],check=True)
raw=out/'lv_draw_label_raw.o'
obj=out/'lv_draw_label_upstream.o'
subprocess.run(flags+['-ffunction-sections','-fdata-sections',
                      '-Dlv_draw_label_iterate_characters=audio_uart_lv_draw_label_48a0be',
                      '-Dlv_draw_unit_draw_letter=audio_uart_lv_draw_unit_draw_letter_48a77e',
                      '-c',str(source),'-o',str(raw)],check=True)
subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',
                '-e','audio_uart_lv_draw_label_48a0be',str(raw),'-o',str(obj)],check=True)
subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True)
aliases=root/'components/main/ambiq_buffer_handlers_candidate_20261014/lvgl_label_aliases.c'
alias_obj=out/'lvgl_label_aliases.o'
subprocess.run(flags+['-c',str(aliases),'-o',str(alias_obj)],check=True)
prior_obj=prior/'candidate.o'
prior_audit=json.loads((prior/'link-audit.json').read_text())
def symbols(path,mode):
    return {line.split()[-1] for line in run(['arm-none-eabi-nm',mode,str(path)]).splitlines()}
defined=(symbols(obj,'-g')-symbols(obj,'-u'))|(symbols(alias_obj,'-g')-symbols(alias_obj,'-u'))
prior_defined=symbols(prior_obj,'-g')-symbols(prior_obj,'-u')
overlap=sorted(defined&prior_defined)
assert not overlap,overlap
candidate=out/'candidate.o'
subprocess.run(['arm-none-eabi-ld','-r',str(prior_obj),str(obj),str(alias_obj),
                '-o',str(candidate)],check=True)
undefined=sorted(symbols(candidate,'-u'))
assert 'audio_uart_lv_draw_label_48a0be' not in undefined
assert 'audio_uart_lv_draw_unit_draw_letter_48a77e' in defined
assert 'audio_uart_ambiq_vector_shape_draw_5202ec' in undefined
assert 'audio_uart_ambiq_label_pixel_53fcc4' not in undefined
audit={'status':'trial Apollo relocatable link with pinned upstream LVGL C source',
       'upstream_submodule':'third-party/upstream/lvgl',
       'upstream_commit':commit,'upstream_source_sha256':sha(source),
       'layout_probe_sha256':sha(probe),'upstream_raw_object_sha256':sha(raw),
       'upstream_object_sha256':sha(obj),'alias_source_sha256':sha(aliases),
       'alias_object_sha256':sha(alias_obj),
       'candidate_object_sha256':sha(candidate),
       'prior_candidate_object_sha256':sha(prior_obj),
       'native_symbols':['audio_uart_lv_draw_label_48a0be',
                         'audio_uart_lv_draw_unit_draw_letter_48a77e'],
       'compile_profile':'Cortex-M55 Thumb; -fshort-enums; LV_CONF_SKIP defaults; only renderer-reachable sections retained',
       'layout_probe':'PASS offsets for label descriptor and task clip area',
       'duplicate_global_definitions':overlap,
       'unresolved_before':prior_audit['integrated_unresolved_after'],
       'unresolved_after':len(undefined),'unresolved_symbols':undefined,
       'source_complete':False,'whole_image_linked':False,
       'limits':['Upstream algorithm/layout alignment is not full native equivalence.',
                 'Mixed enum-size ELF objects emit a linker ABI warning.',
                 'LVGL runtime configuration, global state, and unresolved providers remain.',
                 'No byte equality or hardware proof.']}
(out/'link-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
print('PASS_LVGL_LABEL_SOURCE_TRIAL',len(undefined))
