import logging
from pathlib import Path
from ptlf.config import Settings


def setup(cfg: Settings):
    root = logging.getLogger()
    root.handlers.clear()   # reset (avoid duplicate handlers)
    root.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(ch)

    if cfg.env.lower() in {"dev", "test"}:
        logdir = Path(cfg.data_loc) / "logs"
        logdir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logdir / "flow.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(fh)
        root.info("Logging initialized (flow.log)")
