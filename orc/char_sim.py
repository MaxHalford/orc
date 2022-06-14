import collections
import json
import functools

@functools.cache
def _load_char_sims():
    with open('orc/char_sims.json') as f:
        sims = json.load(f)
    return {tuple(char_pair.split('-')): sim for char_pair, sim in sims.items()}

def sim(a, b):
    char_sims = _load_char_sims()
    try:
        return char_sims[a, b]
    except KeyError:
        return char_sims[b, a]

def top(c, k=5):
    char_sims = _load_char_sims()
    return collections.Counter({
        pair[0] if pair[1] == c else pair[1]: sim
        for pair, sim in char_sims.items()
        if c in pair
    }).most_common(k)

def train_model():

    import pathlib
    from sklearn import datasets
    from sklearn import linear_model
    from sklearn import pipeline
    from sklearn import preprocessing
    import string
    from PIL import Image
    from PIL import ImageFont
    from PIL import ImageDraw
    import numpy as np
    from tqdm import tqdm
    import itertools
    import json
    import pandas as pd
    from scipy.spatial import distance

    # TODO: ideally we should be using a dataset with more characters! Maybe we could just render
    # it ourselves
    X, y = datasets.fetch_openml('mnist_784', version=1, return_X_y=True, as_frame=False)

    model = pipeline.make_pipeline(
        preprocessing.StandardScaler(),
        linear_model.LogisticRegression(
            C=50.0 / len(X),
            penalty="l1",
            solver="saga",
            tol=0.1
        ),
    )

    model.fit(X, y)

    def draw_char(char: str, typeface: str, size: int) -> Image:
        font = ImageFont.truetype(f'{typeface}.ttf', size)
        img = Image.new('L', (size, size))
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), char, 255, font=font)
        return img

    def render(char: str, typeface='Helvetica', size=10) -> np.ndarray:
        img = draw_char(char, typeface=typeface, size=size)
        return np.asarray(img)

    char_imgs = {
        char: render(char, size=28).flatten()
        for char in tqdm(
            string.ascii_letters +
            string.digits +
            string.punctuation
        )
    }

    X = np.vstack(list(char_imgs.values()))
    probas = model.predict_proba(X)
    sims = (
        pd.DataFrame(
            1 - distance.cdist(probas, probas, 'euclidean'),
            columns=list(char_imgs),
            index=list(char_imgs)
        )
        .reset_index()
        .melt(id_vars='index')
    )
    sims.columns = ["c1", "c2", "similarity"]
    sims = sims[sims.eval('c1 != c2')]
    sims = sims.set_index(["c1", "c2"])["similarity"].to_dict()
    sims = {'-'.join(k): v for k, v in sims.items()}
    here = pathlib.Path(__file__).parent
    with open(here / "char_sims.json", 'w') as f:
        json.dump(sims, f, sort_keys=True, indent=4)


if __name__ == "__main__":
    train_model()
