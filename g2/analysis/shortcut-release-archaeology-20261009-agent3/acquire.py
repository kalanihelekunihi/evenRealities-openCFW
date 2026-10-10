#!/usr/bin/env python3
"""Read-only official package metadata acquisition; private output only."""
import concurrent.futures, hashlib, json, pathlib, urllib.request
ROOT = pathlib.Path(__file__).resolve().parent
SOURCES = {
 'keil-pack-index.xml':'https://www.keil.com/pack/index.pidx',
 'cmsis-pdsc.xml':'https://www.keil.com/pack/ARM.CMSIS.pdsc',
 'stm32g0-pdsc.xml':'https://www.keil.com/pack/Keil.STM32G0xx_DFP.pdsc',
 'iar-doc-index.html':'https://docs.iar.com/',
 'nationalchip-software.html':'https://document.nationalchip.com/en/software/software/',
 'infineon-cli.html':'https://documentation.infineon.com/modustoolbox/docs/launching-mtb-capsense-configurator',
 'nationalchip-kws-releases.json':'https://api.github.com/repos/NationalChip/lvp_kws/releases',
 'nationalchip-sed-releases.json':'https://api.github.com/repos/NationalChip/lvp_sed/releases',
 'nationalchip-aiot-releases.json':'https://api.github.com/repos/NationalChip/lvp_aiot/releases',
 'ambiqhal-releases.json':'https://api.github.com/repos/AmbiqMicro/ambiqhal_ambiq/releases',
 'apollo-pdsc.xml':'https://download.ambiq.com/packs/AmbiqMicro.Apollo_DFP.pdsc',
 'cat2-pdsc.xml':'https://itools.infineon.com/cmsis_packs/CAT2_DFP/Infineon.CAT2_DFP.pdsc',
 'arm-compiler-pdsc.xml':'https://www.keil.com/pack/Keil.ARM_Compiler.pdsc',
 'nationalchip-build.html':'https://document.nationalchip.com/en/software/lvp/SDK%E5%BC%80%E5%8F%91%E6%8C%87%E5%8D%97/SDK%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/%E6%90%AD%E5%BB%BA%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83/',
 'iar-arm-index.html':'https://docs.iar.com/ewarm/10.1x/index.html',
 'apollo-1.5.2.pack':'https://download.ambiq.com/packs/AmbiqMicro.Apollo_DFP.1.5.2.pack',
 'iar-dlib.html':'https://docs.iar.com/ewarm/10.1x/en/iar-c-c---development/the-dlib-runtime-environment.html',
 'iar-dlib-intro.html':'https://docs.iar.com/ewarm/10.1x/en/iar-c-c---development/the-dlib-runtime-environment/introduction-to-the-runtime-environment.html',
}
def acquire(item):
 name,url=item
 try:
  request=urllib.request.Request(url,headers={'User-Agent':'OpenCFW-reference-metadata-audit'})
  with urllib.request.urlopen(request,timeout=40) as response:
   body=response.read(); final=response.url; status=response.status
  (ROOT/'acquisitions'/name).write_bytes(body)
  return dict(path='acquisitions/'+name,url=url,final_url=final,status=status,size=len(body),sha256=hashlib.sha256(body).hexdigest())
 except Exception as error:
  return dict(url=url,path=None,error=str(error))
if __name__=='__main__':
 (ROOT/'acquisitions').mkdir(exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
  records=list(pool.map(acquire,SOURCES.items()))
 (ROOT/'acquisition.json').write_text(json.dumps(records,indent=2)+'\n')
 print(json.dumps(records,indent=2))
