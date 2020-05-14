def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('organs', '/organs')
    config.add_route('organsId', '/organs/{itemId}')
