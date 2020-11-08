from typing import List, Callable, Dict, Type

from bolinette import core, blnt, web


class BolinetteCache:
    def __init__(self):
        self.models: Dict[str, Type['blnt.Model']] = {}
        self.mixins: Dict[str, Type['blnt.Mixin']] = {}
        self.services: Dict[str, Type['blnt.Service']] = {}
        self.controllers: Dict[str, Type['web.Controller']] = {}
        self.topics: Dict[str, Type['web.Topic']] = {}
        self.init_funcs: List[Callable[['core.BolinetteContext'], None]] = []
        self.seeders = []


cache = BolinetteCache()
