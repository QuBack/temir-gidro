"""301 redirects from the old site's addresses (temir-gidro.ru on WordPress) to the new ones.

The old pages are in Yandex and Google and linked from other sites; a permanent redirect keeps
their visitors and passes their weight to the new page. The list: the old site's menu and footer
(pages saved in 2026-10), its audit and Google Search Console's 51 indexed pages (2026-10-23);
its 12 not-found ones; add the rest from Yandex.Webmaster.
Keys are decoded paths without the trailing slash, so «/about-us» and «/about-us/» both match.
"""

from django.http import HttpResponsePermanentRedirect

OLD_TO_NEW = {
    # Lifts
    "/equipment": "/podemniki/",
    "/equipment/temir-gidro-1x": "/podemniki/nozhnichnye/1x/",
    "/equipment/temir-gidro-x2": "/podemniki/nozhnichnye/2x/",
    "/equipment/temir-gidro-2x": "/podemniki/nozhnichnye/2x/",
    "/equipment/temir-gidro-3x": "/podemniki/nozhnichnye/3x/",
    "/equipment/temir-gidro-4x": "/podemniki/nozhnichnye/4x/",
    "/equipment/temir-gidro-console": "/podemniki/konsolnye/1l/",
    "/equipment/auto-lifts": "/podemniki/chetyrehstoechnye/",
    "/equipment/transport-lift": "/podemniki/avtomobilnye/",
    "/equipment/waste-container-lifter": "/podemniki/dlya-musornyh-kontejnerov/",
    "/equipment/podemniki-dlya-okrasochnyh-kamer": "/podemniki/dlya-okrasochnyh-kamer/1x/",
    "/equipment/подъемники-для-окрасочных-камер-2d": "/podemniki/dlya-okrasochnyh-kamer/2d/",
    "/equipment/подъемники-для-окрасочных-камер-3d": "/podemniki/dlya-okrasochnyh-kamer/3d/",
    # Accessories: cylinders and power units have pages, the other parts are in the lifts' kits.
    "/accessories": "/podemniki/",
    "/accessories/gidraulic-cylinders": "/gidrocilindry/",
    "/accessories/oil-station": "/gidrostancii/",
    "/accessories/station-control": "/gidrostancii/",
    "/accessories/end-switch": "/podemniki/",
    "/accessories/oilers": "/podemniki/",
    "/accessories/overload-protection": "/podemniki/",
    "/accessories/strong-plate": "/podemniki/",
    "/accessories/top-plate": "/podemniki/",
    "/accessories/mechanic-blocks": "/podemniki/",
    "/accessories/remote-control": "/podemniki/",
    "/accessories/rollover-protection": "/podemniki/",
    "/accessories/safe-frame": "/podemniki/",
    "/accessories/safety-valves": "/podemniki/",
    "/accessories/service-hatch": "/podemniki/",
    "/accessories/speed-adjusters": "/podemniki/",
    "/accessories/vibration-supports": "/podemniki/",
    # Company, request form, blog
    "/about-us": "/o-kompanii/",
    "/order": "/zayavka/",
    "/blog": "/stati/",
    "/ножничный-подъемник-для-автосервиса": "/stati/nozhnichnyj-podemnik-dlya-avtoservisa/",
    "/ножничные-подъемники": "/podemniki/nozhnichnye/",
    "/подбор-гидроцилиндров": "/gidrocilindry/",
    # Blog categories and tags: tags named after a product go to its page, the rest to the articles.
    "/category/news": "/stati/",
    "/category/our-production": "/o-kompanii/",
    "/category/reviews": "/stati/",
    "/category/без-рубрики": "/stati/",
    "/tag/scissors": "/podemniki/nozhnichnye/",
    "/tag/consoles": "/podemniki/konsolnye/",
    "/tag/pillars": "/podemniki/chetyrehstoechnye/",
    "/tag/transports": "/podemniki/avtomobilnye/",
    "/tag/cilinders": "/gidrocilindry/",
    "/tag/complect": "/podemniki/",
    "/tag/machines": "/podemniki/",
    "/tag/automatization": "/stati/",
    "/tag/robotization": "/stati/",
    "/tag/expo": "/stati/",
    # Search Console's 404s (2026-10-23): addresses already gone on the old site but still linked
    # from elsewhere, so they are worth catching too.
    "/statsionarnye-nozhnichnye-podyemniki": "/podemniki/nozhnichnye/",
    "/statsionarnye-nozhnichnye-podyemniki/nozhnichnyy-1x": "/podemniki/nozhnichnye/1x/",
    "/statsionarnye-nozhnichnye-podyemniki/nozhnichnyy-3x": "/podemniki/nozhnichnye/3x/",
    "/nozhnichnyy-podemnik": "/podemniki/nozhnichnye/",
    "/chetyrekhopornye-podemniki": "/podemniki/chetyrehstoechnye/",
    "/konsolnye-podyomniki": "/podemniki/konsolnye/",
    "/podyomniki-dlya-tehniki": "/podemniki/avtomobilnye/",
    "/oborudovanie": "/podemniki/",
    "/oborudovanie/nozhnichnye-podemniki-preimushchestva-primenenie-i-vybor-proizvoditelya-temir-gidro":
        "/stati/kak-vybrat-nozhnichnyj-podemnik/",
    "/oborudovanie/tehnicheskie-osobennosti-avtomobilnyh-liftov": "/podemniki/avtomobilnye/",
    "/news": "/stati/",
    # News about exhibitions: not moved yet (no texts), the articles section instead.
    "/cemat-russia-2025": "/stati/",
    "/lift-expo-russia-2025": "/stati/",
    "/russian-prom-2025": "/stati/",
}


class OldSiteRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path.rstrip("/").lower() or "/"
        target = OLD_TO_NEW.get(path)
        if target:
            query = request.META.get("QUERY_STRING")
            return HttpResponsePermanentRedirect(f"{target}?{query}" if query else target)
        return self.get_response(request)
