"""Reuse the approved standalone 2L viewer for the separate 4X result."""
from pathlib import Path
ROOT=Path(r'C:\projects\temir-gidro')
html=(ROOT/'docs/models/2l/index.html').read_text(encoding='utf-8')
html=html.replace('2L','4X').replace('/2l/','/4x/').replace('2l.glb','4x.glb').replace('2l.blend','4x-working.blend')
html=html.replace('Консольный подъёмник · 2 мачты','Ножничный подъёмник · 4 яруса')
html=html.replace('Консольный подъёмник 4X: две красные мачты, металлические цепи и тёмная грузовая платформа',
                  'Ножничный подъёмник 4X: четыре яруса красных ножниц, металлические штоки, тёмные основание и платформа')
html=html.replace('Цепи и штоки · металл','Штоки и крепёж · металл').replace('Платформа и защитные панели','Основание и платформа')
html=html.replace('2l2.max / сборка 2l2','2l2.max / сборка 4X2L')
html=html.replace('3,16 × 3,10 × 15,02 м','2,25 × 1,91 × 6,08 м')
html=html.replace('Высота мачт сохранена из исходного MAX. Цвета и материалы восстановлены по изображениям каталога.',
                  'Геометрия четырёх ярусов сохранена из исходного MAX. Цвета, металл и настил восстановлены по изображению каталога.')
html=html.replace('camera-orbit="40deg 78deg auto"','camera-orbit="30deg 78deg auto"').replace('data-orbit="40deg 78deg auto"','data-orbit="30deg 78deg auto"')
lines=html.splitlines()
for i,line in enumerate(lines):
    if '<section class="panel"><h2>Изображения для сверки' in line:
        lines[i]='''        <section class="panel"><h2>Изображение для сверки</h2><div class="reference" style="grid-template-columns:1fr"><a href="../../../static/img/catalog/nozhnichnyj-podemnik-4x-800.webp" target="_blank" rel="noopener"><img src="../../../static/img/catalog/nozhnichnyj-podemnik-4x-400.webp" style="height:360px" alt="Ножничный подъёмник 4X: изображение из каталога"></a></div><p class="caption">Эталон из каталога. Нажмите, чтобы открыть крупнее.</p></section>'''
html='\n'.join(lines)+'\n'
html=html.replace('<button type="button" id="rotate"',
    '<button type="button" data-orbit="30deg 35deg 7.2m" data-target="0m 6.08m 0m" aria-pressed="false">Настил</button><button type="button" id="rotate"')
html=html.replace("viewer.cameraOrbit=b.dataset.orbit;viewer.fieldOfView='30deg';",
    "viewer.cameraTarget=b.dataset.target||'auto auto auto';viewer.cameraOrbit=b.dataset.orbit;viewer.fieldOfView='30deg';")
html=html.replace('href="4x.glb"','href="4x.glb?v=deck-3"').replace('src="4x.glb"','src="4x.glb?v=deck-3"')
html=html.replace("fetch('4x.glb'","fetch('4x.glb?v=deck-3'")
# Navigation keeps each result on its own page.
html=html.replace('<div class="tag">Модели оборудования / отдельный просмотр</div>',
                  '<nav class="tag" aria-label="Модели оборудования"><a href="../2l/" style="color:inherit">Модель 2L</a> &nbsp; / &nbsp; <strong aria-current="page">Модель 4X</strong></nav>')
(ROOT/'docs/models/4x/index.html').write_text(html,encoding='utf-8')
