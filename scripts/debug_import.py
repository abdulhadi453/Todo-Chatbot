import sys
import importlib
print('sys.path:')
for i, p in enumerate(sys.path[:10]):
    print(i, p)
print('\nfind_spec todo_backend:', importlib.util.find_spec('todo_backend'))
print('find_spec todo_backend.src:', importlib.util.find_spec('todo_backend.src'))
print('find_spec todo_backend.src.config:', importlib.util.find_spec('todo_backend.src.config'))
try:
    import todo_backend.src.config.database as db
    print('\nImported db module:', db)
except Exception as e:
    print('\nImport error:', type(e), e)
