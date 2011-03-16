# coding: utf8
import os
import stat
import time

ps = os.path.join(request.folder,'sessions')
try: [os.unlink(os.path.join(ps,f)) for f in os.listdir(ps) if os.stat (os.path.join(ps,f))[stat.ST_MTIME]<time.time()-3600]
except: pass
