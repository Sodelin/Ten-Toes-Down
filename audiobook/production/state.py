"""Short, locked queue edits shared by preparation, rendering and publication."""
from contextlib import contextmanager
import json, msvcrt, os, tempfile, time
from pathlib import Path

@contextmanager
def publication_lock(log_root):
    """Serialize chapter/book release uploads and shared Git checkout writes."""
    path=Path(log_root)/'publication.lock'
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a+b') as handle:
        if handle.seek(0,2)==0:
            handle.write(b'0'); handle.flush()
        deadline=time.monotonic()+1800
        while True:
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError:
                if time.monotonic()>deadline:
                    raise TimeoutError('Another GitHub publication stayed busy for 30 minutes.')
                time.sleep(1)
        try:
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)

@contextmanager
def locked_progress(path):
    path=Path(path)
    lock=path.with_suffix('.lock')
    lock.parent.mkdir(parents=True,exist_ok=True)
    with lock.open('a+b') as handle:
        if handle.seek(0,2)==0:
            handle.write(b'0'); handle.flush()
        deadline=time.monotonic()+30
        while True:
            handle.seek(0)
            try:
                msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
                break
            except OSError:
                if time.monotonic()>deadline: raise TimeoutError('Progress queue lock stayed busy.')
                time.sleep(.1)
        try:
            data=json.loads(path.read_text(encoding='utf-8-sig'))
            yield data
            with tempfile.NamedTemporaryFile('w',encoding='utf-8',newline='\n',dir=path.parent,suffix='.part',delete=False) as temp:
                json.dump(data,temp,indent=2,ensure_ascii=False)
                temp.write('\n'); temp.flush(); os.fsync(temp.fileno())
                temporary=Path(temp.name)
            temporary.replace(path)
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(),msvcrt.LK_UNLCK,1)
