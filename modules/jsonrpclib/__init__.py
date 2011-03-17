from applications.shared.modules.jsonrpclib.config import Config
config = Config.instance()
from applications.shared.modules.jsonrpclib.history import History
history = History.instance()
from applications.shared.modules.jsonrpclib.jsonrpc import Server, MultiCall, \
        Fault, ProtocolError, loads, dumps
