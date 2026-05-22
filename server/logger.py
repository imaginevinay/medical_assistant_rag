import logging

def setup_logger(name="MedicalAssistant"):
    logger=logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    formatter=logging.Formatter("[%(asctime)s] [%(levelname)s] --- [%(message)s]")
    ch.setFormatter(formatter)
    
    # if any module does not has logger module attached then only add logger handler
    if not logger.hasHandlers():
        logger.addHandler(ch)
        
    return logger

logger = setup_logger()

# logger.info('RAG process started')
# logger.debug('RAG process debug')
# logger.error('RAG process started')
# logger.critical('RAG process started')