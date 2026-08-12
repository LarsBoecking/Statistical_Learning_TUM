import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from src.figures import RED, GREEN

def load_geo(df, types=None):
    """Load EM-DAT natural-disaster records with valid coordinates."""
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df = df[df["Latitude"].between(-90, 90) & df["Longitude"].between(-180, 180)]
    types = types or ["Earthquake", "Flood", "Storm", "Volcanic activity"]
    return df[df["Disaster Type"].isin(types)], types

def sigmoid(z): return 1/(1+np.exp(-z))
def tanh(z): return np.tanh(z)
def relu(z): return np.maximum(0, z)


def _L1d(w):
    return 0.03 * w ** 4 - 0.55 * w ** 2 + 0.25 * w + 4.0

def _dL1d(w):
    return 0.12 * w ** 3 - 1.10 * w + 0.25

_wg = np.linspace(-5, 5, 20001)

_Lg = _L1d(_wg)

_mins = _wg[1:-1][(_Lg[1:-1] < _Lg[:-2]) & (_Lg[1:-1] < _Lg[2:])]

GLOBAL_W = _mins[np.argmin(_L1d(_mins))]

LOCAL_W = _mins[np.argmax(_L1d(_mins))]

_SS_SPECS = [(0.010, "too small", RED, 0.1), (0.12, "well chosen", GREEN, -4.2), (1.35, "too large", RED, -4.2)]

def _ss_path(eta, w0, n):
    w = w0; pts = [w]
    for _ in range(n):
        w = w - eta * _dL1d(w); w = np.clip(w, -5.4, 5.4); pts.append(w)
    return np.array(pts)

def _S3(a, b):
    return a ** 3 - 3 * a * b ** 2

def _g3(p):
    return np.array([3 * p[0] ** 2 - 3 * p[1] ** 2, -6 * p[0] * p[1]])

_R = 1.25

_A3 = np.linspace(-_R, _R, 120)

_B3 = np.linspace(-_R, _R, 120)

_AA3, _BB3 = np.meshgrid(_A3, _B3)

_AA3, _BB3 = np.meshgrid(_A3, _B3)

_ZZ3 = _S3(_AA3, _BB3)

_ZOFF = 0.55

def _z_on(path):
    return np.array([_S3(x, y) for x, y in path]) + _ZOFF

def _surf3d(ax):
    ax.plot_surface(_AA3, _BB3, _ZZ3, cmap="viridis", alpha=1.0, linewidth=0,
                    antialiased=True, rcount=120, ccount=120)
    ax.set_xlabel("$\\theta_1$"); ax.set_ylabel("$\\theta_2$"); ax.set_zlabel(r"$R(\theta)$")
    ax.set_zlim(_ZZ3.min() - 0.2, _ZZ3.max() + 0.6)
    ax.view_init(elev=38, azim=-52)

def _bowl(A, B):
    return 0.5 * A ** 2 + 1.3 * B ** 2

def _grad(a, b):
    return np.array([a, 2.6 * b])