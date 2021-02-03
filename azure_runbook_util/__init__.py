import logging
import sys

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format="[%(asctime)s] %(name)s %(levelname)s %(module)s %(message)s")
