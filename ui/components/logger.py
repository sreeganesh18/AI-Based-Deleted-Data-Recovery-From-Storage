import logging
import streamlit as st

class StreamlitLogHandler(logging.Handler):
    """
    A custom logging handler that appends log records to st.session_state.logs.
    This allows logs to persist across reruns and be displayed in the UI.
    """
    def emit(self, record):
        try:
            msg = self.format(record)
            # Ensure we are in a context where session_state is accessible
            if "logs" in st.session_state:
                st.session_state.logs.append(msg)
                # Keep only last 500 logs to prevent session state bloat
                if len(st.session_state.logs) > 500:
                    st.session_state.logs.pop(0)
        except Exception:
            self.handleError(record)

def setup_streamlit_logging(name=None):
    """
    Configures the logger with the StreamlitLogHandler.
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers to the same logger
    if not any(isinstance(h, StreamlitLogHandler) for h in logger.handlers):
        handler = StreamlitLogHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger
