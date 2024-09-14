def stringify(*args, **kwargs):
    def stringify_obj(obj):
        if obj is None:
            return "None"
        if isinstance(obj, str):
            return f"'{obj}'"
        if isinstance(obj, (int, float, bool)):
            return str(obj)
        if isinstance(obj, (list, tuple)):
            return '[' + ', '.join(stringify_obj(item) for item in obj) + ']'
        if isinstance(obj, dict):
            return '{' + ', '.join(f"{stringify_obj(k)}: {stringify_obj(v)}" for k, v in obj.items()) + '}'
        return str(obj)  # Fallback for other object types

    # Join args and kwargs for logging
    result = [stringify_obj(arg) for arg in args]
    for name, value in kwargs.items():
        result.append(f"{name}: {stringify_obj(value)}")
    return ', '.join(result)