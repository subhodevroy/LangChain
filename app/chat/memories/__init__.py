from .sql_memory import build_memory
from .window_memory import window_buffer_memory
memory_map={
    "sql_buffer_memory": build_memory,
    "sql_window_buffer_memory": window_buffer_memory
}