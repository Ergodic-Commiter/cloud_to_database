import logging
from pathlib import Path
from ptlf import core



class ContextAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = {**getattr(self, 'extra', {}), **kwargs.get('extra', {})}
        kwargs['extra'] = extra
        return msg, kwargs


def setup(cfg:core.Settings):
    root = logging.getLogger()
    root.handlers.clear()   # reset (avoid duplicate handlers)
    root.setLevel(logging.INFO)
    
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    root.addHandler(ch)

    if cfg.env.lower() in {"dev", "test"}:
        logdir = Path(cfg.data_loc)/"logs"
        logdir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(logdir / "flow.log", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        root.addHandler(fh)
        root.info("Logging initialized (flow.log)")


def get_logger(name:str=None, **context) -> logging.LoggerAdapter: 
    dot_name = f".{name}" if name else ""
    base = logging.getLogger("ptlf"+dot_name)
    return ContextAdapter(base, context)
