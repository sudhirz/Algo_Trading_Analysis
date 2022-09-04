
import pandas as pd

def get_adx(High, Low, Close, lookback):
    plus_dm = High.diff()
    minus_dm = Low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0

    tr1 = pd.DataFrame(High - Low)
    tr2 = pd.DataFrame(abs(High - Close.shift(1)))
    tr3 = pd.DataFrame(abs(Low - Close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(lookback).mean()

    plus_di = 100 * (plus_dm.ewm(alpha=1 / lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha=1 / lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha=1 / lookback).mean()
    return plus_di, minus_di, adx_smooth