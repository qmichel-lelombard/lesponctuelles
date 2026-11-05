"""Format story 1080x1920 à partir des visuels 1080x1350 : python3 story.py

Le fond crème est uni sur les bords : on prolonge le visuel en haut et en bas et on le centre.
Tout le contenu reste dans les zones sûres Instagram (≈250 px en haut, ≈300 px en bas).
"""
import glob, os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920
CREME = (248, 247, 242)
out_dir = os.path.join(HERE, 'sorties', 'story'); os.makedirs(out_dir, exist_ok=True)
for f in sorted(glob.glob(os.path.join(HERE, 'sorties', 'jour*.png'))):
    im = Image.open(f).convert('RGB')
    st = Image.new('RGB', (W, H), CREME)
    st.paste(im, (0, (H - im.height) // 2))
    o = os.path.join(out_dir, os.path.basename(f).replace('.png', '_story.png'))
    st.save(o); print(o)
