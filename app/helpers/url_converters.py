from werkzeug.routing import BaseConverter

# Converter regex
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map, *items)
        self.regex = items[0]

# Converter for UUID gen from helper
class UUIDConverter(BaseConverter):
    regex = "[0-9a-z]{22}"