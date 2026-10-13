import sys, glob, os, asyncio, re
from playwright.async_api import async_playwright
from PIL import Image
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        for f in sorted(glob.glob(src + '/*.svg')):
            svg = open(f).read()
            W, H = map(int, re.search(r'width="(\d+)" height="(\d+)"', svg).groups())
            await pg.set_viewport_size({'width': W, 'height': H})
            await pg.set_content(f'<html><body style="margin:0">{svg}</body></html>')
            png = f'{out}/{os.path.basename(f)[:-4]}.png'
            await pg.screenshot(path=png, clip={'x':0,'y':0,'width':W,'height':H})
            Image.open(png).convert('RGB').save(png[:-4] + '.jpg', quality=92, optimize=True, progressive=True)
            os.remove(png)
        await b.close()
asyncio.run(main())
