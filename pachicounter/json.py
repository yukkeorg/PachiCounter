try:
    import orjson as json
except ImportError:
    try:
        import ujson as json  # ty: ignore[unresolved-import]
    except ImportError:
        import json
