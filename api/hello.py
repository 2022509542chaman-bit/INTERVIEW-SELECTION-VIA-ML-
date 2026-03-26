def handler(request):
    return {"hello": "world", "path": request.get("path", "/")}
