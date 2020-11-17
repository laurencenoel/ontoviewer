def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('organs', '/organs')
    config.add_route('organs_comp', '/organs_comp')
    config.add_route('cells', '/cells')
    config.add_route('cells_comp', '/cells_comp')
    config.add_route('stages', '/stages')
