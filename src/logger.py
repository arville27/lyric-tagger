import logging
import sys

# Create a custom logger
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# Create handlers
c_handler = logging.StreamHandler(stream=sys.stdout)
f_handler = logging.FileHandler(filename='log/app.log', encoding='utf-8')

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
c_handler.setFormatter(log_format)
f_handler.setFormatter(log_format)

# Add handlers to the logger
log.addHandler(c_handler)
log.addHandler(f_handler)
