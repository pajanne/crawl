SELECT feature.uniquename, feature.name FROM feature WHERE feature.uniquename ~* %(term)s or feature.name ~* %(term)s

