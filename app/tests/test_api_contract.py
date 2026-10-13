from app.main import app


def test_every_non_health_api_route_requires_bearer_security_scheme():
    schema = app.openapi()
    public_paths = {
        "/api/v1/auth/login",
        "/api/v1/auth/refresh",
        "/api/v1/auth/password-reset/request",
        "/api/v1/auth/password-reset/confirm",
    }
    for path, operations in schema["paths"].items():
        if path == "/health" or path in public_paths:
            continue
        for operation in operations.values():
            if isinstance(operation, dict) and path.startswith("/api/v1/"):
                assert operation.get("security"), path


def test_private_files_are_not_exposed_as_static_route():
    assert not any(getattr(route, "path", "").startswith("/private_storage") for route in app.routes)
