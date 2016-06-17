class Error(Exception):
    pass


class TunnelInstanceError(Error):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message


class TunnelManagerError(Error):

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
